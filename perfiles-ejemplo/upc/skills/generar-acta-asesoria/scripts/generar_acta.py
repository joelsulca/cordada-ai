#!/usr/bin/env python3
"""
Genera la siguiente Acta de Reunión (Word) de una asesoría semanal, a partir del
acta anterior más reciente y de los apuntes de sesión que el docente envía por correo.
Ejemplo del perfil UPC: el formato del acta (tablas "Código y Nombre del Proyecto",
agenda, compromisos y firmas) es el de las actas de asesoría de proyectos de la UPC.

Por qué funciona así: la plantilla del acta es un .docx oficial de la universidad
(tablas con estilos, márgenes, fuentes específicas). Recrearla desde cero con
python-docx es frágil y probablemente no calce visualmente. En cambio, partir del
acta anterior y editar solo el texto que cambia conserva el formato exacto sin
tener que reconstruirlo.

Uso típico:

    python3 generar_acta.py \
        --previous "deliverables/actas/CURSO-CODIGO-Acta-03.docx" \
        --output   "deliverables/actas/CURSO-CODIGO-Acta-04.docx" \
        --numero 4 \
        --fecha 22/09/2026 \
        --apuntes apuntes_semana4.txt \
        --fecha-maxima-compromisos 29/09/2026

El archivo de apuntes debe tener el mismo formato que el correo del profesor,
por ejemplo:

    Agenda
    -Revisión de Objetivos específicos
    -Revisión de formato propuesto para trabajo profesional ágil

    Compromisos
    -Presentación de avances (Proyecto)
    -Revisión de artefactos de gestión (Asesor)

Lo más fácil es copiar y pegar el cuerpo del correo del profesor tal cual a un
archivo .txt y pasarlo con --apuntes. No hace falta limpiarlo a mano.
"""

import argparse
import copy
import re
import shutil
import sys
from pathlib import Path

import docx
from docx.oxml.ns import qn


# ---------------------------------------------------------------------------
# Parseo de los apuntes del profesor
# ---------------------------------------------------------------------------

def parse_apuntes(texto: str):
    """Extrae Agenda y Compromisos del texto del correo del profesor.

    La Agenda es una lista simple de temas. Los Compromisos vienen con el
    responsable pegado al final entre paréntesis, ej.:
        "Presentación LLM & RAG (Asesor)"
    Ese paréntesis se separa y se coloca en su propia columna "Responsable".
    Ojo: en el Acta 02 ya enviada este mapeo se hizo al revés en las 3 filas
    (donde el correo decía "(Proyecto)" se puso "Asesor" y viceversa) — por
    eso este parser existe, para no depender de transcribir el paréntesis a mano.
    """
    lines = [l.strip() for l in texto.splitlines()]

    def section(name):
        items = []
        capturing = False
        for line in lines:
            if re.match(rf'^{name}\s*:?\s*$', line, re.IGNORECASE):
                capturing = True
                continue
            if capturing:
                if not line:
                    if items:
                        break
                    continue
                # nueva sección empieza (ninguno de los guiones)
                if re.match(r'^(agenda|compromisos)\s*:?\s*$', line, re.IGNORECASE):
                    break
                bullet = re.match(r'^[-•*]\s*(.+)$', line)
                if bullet:
                    items.append(bullet.group(1).strip())
                else:
                    items.append(line)
        return items

    agenda = section('agenda')
    compromisos_raw = section('compromisos')

    compromisos = []
    for item in compromisos_raw:
        m = re.match(r'^(.*)\(([^)]+)\)\s*$', item)
        if m:
            acuerdo, responsable = m.group(1).strip(), m.group(2).strip()
        else:
            acuerdo, responsable = item, None
        compromisos.append((acuerdo, responsable))

    return agenda, compromisos


# ---------------------------------------------------------------------------
# Helpers de edición docx
# ---------------------------------------------------------------------------

def set_cell_text(cell, text):
    """Reemplaza el texto de una celda preservando el formato del primer run.

    Muchas celdas de esta plantilla tienen el texto partido en varios runs
    (ej. una fecha "08/09/2026" repartida en 6 runs). Escribir todo en el
    primer run y vaciar el resto evita dejar fragmentos del texto viejo
    mezclados con el nuevo.
    """
    p = cell.paragraphs[0]
    runs = p.runs
    if not runs:
        p.add_run(text)
        return
    runs[0].text = text
    for r in runs[1:]:
        r.text = ""


def find_table(doc, header_substring):
    """Ubica una tabla por un texto que aparezca en su primera fila.

    Más robusto que indexar tablas por posición: si el profesor reordena o
    agrega una tabla nueva a la plantilla el año que viene, esto se sigue
    encontrando por contenido en vez de romperse silenciosamente.
    """
    for t in doc.tables:
        header_text = " ".join(c.text for c in t.rows[0].cells)
        if header_substring.lower() in header_text.lower():
            return t
    raise ValueError(f"No se encontró ninguna tabla con '{header_substring}' en el encabezado")


def set_table_rows(table, rows_data, start_col_texts):
    """Ajusta una tabla de N filas de datos (sin contar el header) al tamaño
    de rows_data, agregando o quitando filas según haga falta, y llena cada
    fila con start_col_texts(i, row_values) -> lista de textos por columna.
    """
    n_needed = len(rows_data)
    n_have = len(table.rows) - 1  # sin header

    # agregar filas si faltan, copiando la última fila de datos: table.add_row()
    # crea filas sin el alto, la alineación ni la fuente de la plantilla
    # (Acta 10: las filas 2 y 3 de la agenda salieron sin formato)
    while n_have < n_needed:
        if n_have > 0:
            table._tbl.append(copy.deepcopy(table.rows[-1]._tr))
        else:
            table.add_row()
        n_have += 1

    # quitar filas sobrantes (de abajo hacia arriba)
    while n_have > n_needed:
        tr = table.rows[-1]._tr
        tr.getparent().remove(tr)
        n_have -= 1

    for i, row_values in enumerate(rows_data):
        row = table.rows[i + 1]
        texts = start_col_texts(i, row_values)
        for cell, text in zip(row.cells, texts):
            set_cell_text(cell, text)


def strip_signatures(doc):
    """Elimina todas las firmas (imágenes pegadas o firmas a lápiz/ink) del
    acta anterior antes de guardar la nueva.

    Ojo: no todas las firmas están dentro de la tabla de firmas. Algunas
    quedan como párrafos flotantes/anclados en el cuerpo del documento,
    justo antes de la tabla, con posición absoluta que las hace *verse*
    dentro de la tabla aunque estructuralmente no lo estén. Por eso hay que
    buscar <w:drawing> y <w:pict> en TODO el body, no solo en la tabla de
    firmas, y borrar el <w:p> que los contiene (si el párrafo no tiene más
    texto que el dibujo) o el <w:r> puntual (si comparte párrafo con texto
    que sí hay que conservar, como el nombre o el rol del firmante).
    """
    body = doc.element.body
    removed = 0

    for p in list(body.iter(qn('w:p'))):
        drawings = list(p.iter(qn('w:drawing'))) + list(p.iter(qn('w:pict')))
        if not drawings:
            continue
        texto_parrafo = "".join(t.text or "" for t in p.iter(qn('w:t')))
        if texto_parrafo.strip():
            # el párrafo tiene texto real (nombre/rol) además del dibujo:
            # borrar solo los runs que contienen el dibujo
            for r in list(p.iter(qn('w:r'))):
                if r.find(qn('w:drawing')) is not None or r.find(qn('w:pict')) is not None:
                    r.getparent().remove(r)
                    removed += 1
        else:
            # párrafo vacío salvo por el dibujo (típico de firmas ancladas
            # flotando fuera de la tabla): se puede borrar entero
            parent = p.getparent()
            if parent is not None:
                parent.remove(p)
                removed += 1

    return removed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--previous', required=True, help='.docx del acta anterior más reciente')
    ap.add_argument('--output', required=True, help='ruta del nuevo .docx a generar')
    ap.add_argument('--numero', required=True, type=int, help='número de acta = número de semana de asesoría')
    ap.add_argument('--fecha', required=True, help='fecha de la reunión, formato DD/MM/AAAA')
    ap.add_argument('--hora-inicio', default=None, help='si no se pasa, se mantiene la del acta anterior')
    ap.add_argument('--hora-fin', default=None, help='si no se pasa, se mantiene la del acta anterior')
    ap.add_argument('--codigo-proyecto', default=None, help='si no se pasa, se mantiene el del acta anterior')
    ap.add_argument('--nombre-proyecto', default=None,
                     help='nombre del proyecto sin el código (si no se pasa, se mantiene el del acta anterior)')
    ap.add_argument('--apuntes', required=True, help='archivo .txt con el correo de apuntes del profesor (Agenda + Compromisos)')
    ap.add_argument('--fecha-maxima-compromisos', required=True,
                     help='fecha límite (DD/MM/AAAA) a aplicar a todos los compromisos, normalmente un día antes de la siguiente sesión')
    args = ap.parse_args()

    previous = Path(args.previous)
    output = Path(args.output)
    if not previous.exists():
        sys.exit(f"No existe el acta anterior: {previous}")

    shutil.copyfile(previous, output)
    doc = docx.Document(str(output))

    apuntes_texto = Path(args.apuntes).read_text(encoding='utf-8')
    agenda, compromisos = parse_apuntes(apuntes_texto)

    if not agenda:
        sys.exit("No se encontraron temas de Agenda en el archivo de apuntes. Revisa el formato (ver docstring del script).")
    if not compromisos:
        sys.exit("No se encontraron Compromisos en el archivo de apuntes. Revisa el formato (ver docstring del script).")

    sin_responsable = [a for a, r in compromisos if r is None]
    if sin_responsable:
        print("AVISO: estos compromisos no traían responsable entre paréntesis en el correo; "
              "revisa el .docx generado y complétalo a mano:")
        for a in sin_responsable:
            print(f"  - {a}")

    # 1. Título: "Acta de Reunión NN"
    # El número puede venir partido en varios runs (ej. "0" y "3" por separado
    # para "03"), así que hay que juntarlos en uno solo con el número nuevo y
    # vaciar los demás — reemplazar cada run por separado duplicaría el número
    # (ej. "03" -> "4" en cada run -> "44").
    title_p = doc.paragraphs[0]
    digit_runs = [r for r in title_p.runs if re.fullmatch(r'\d+', r.text.strip() or '')]
    if digit_runs:
        digit_runs[0].text = f"{args.numero:02d}"
        for r in digit_runs[1:]:
            r.text = ""

    # 2. Tabla de información general
    info_table = find_table(doc, "Código y Nombre del Proyecto")
    info_row = info_table.rows[1]
    if args.codigo_proyecto or args.nombre_proyecto:
        actual = info_row.cells[0].text
        codigo_actual, _, nombre_actual = actual.partition(' - ')
        codigo = args.codigo_proyecto or codigo_actual.strip()
        nombre = args.nombre_proyecto or nombre_actual.strip()
        set_cell_text(info_row.cells[0], f"{codigo} - {nombre}")
    set_cell_text(info_row.cells[1], args.fecha)
    if args.hora_inicio:
        set_cell_text(info_row.cells[2], args.hora_inicio)
    if args.hora_fin:
        set_cell_text(info_row.cells[3], args.hora_fin)

    # 3. Agenda
    agenda_table = find_table(doc, "Temas")
    set_table_rows(
        agenda_table, agenda,
        lambda i, tema: [str(i + 1), tema],
    )

    # 4. Compromisos
    compromisos_table = find_table(doc, "Acuerdos")
    set_table_rows(
        compromisos_table, compromisos,
        lambda i, item: [str(i + 1), item[0], item[1] or "", args.fecha_maxima_compromisos],
    )

    # 5. Quitar firmas del acta anterior
    removed = strip_signatures(doc)

    doc.save(str(output))

    # 6. Verificación final
    xml = docx.Document(str(output)).element.body.xml
    quedan_dibujos = xml.count("<w:drawing") + xml.count("<w:pict")

    print(f"Acta generada: {output}")
    print(f"Agenda: {len(agenda)} temas | Compromisos: {len(compromisos)} ítems")
    print(f"Firmas/dibujos eliminados: {removed} | Quedan en el documento: {quedan_dibujos}")
    if quedan_dibujos:
        print("ADVERTENCIA: quedaron dibujos sin eliminar. Revisa el .docx manualmente antes de firmar.")


if __name__ == '__main__':
    main()
