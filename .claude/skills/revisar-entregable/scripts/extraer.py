"""Convierte entregables (.docx, .xlsx) a texto que un revisor pueda leer y citar, sin pasar por LibreOffice.

Uso (desde la raíz del repositorio):
    python3 -I .claude/skills/revisar-entregable/scripts/extraer.py \
        <archivo.docx | archivo.xlsx> [...] --out <carpeta>

Por cada .docx escribe <nombre>.md con:
- Títulos con su nivel (# a ####) según el estilo del párrafo (Título 1 a 4, Heading 1 a 4).
- Cada párrafo con su número [¶N] para citarlo y su estilo cuando no es el normal.
- Tablas en Markdown, con [TABLA k] y el número de párrafo donde empiezan.
- Imágenes como [IMAGEN: nombre], hipervínculos como [texto](url), resaltados como ==texto==.
- Comentarios y control de cambios, si los hay.
Y <nombre>.chequeos.md con comprobaciones mecánicas: títulos vacíos, texto resaltado, marcadores entre corchetes,
rótulos de tablas y figuras con su numeración, palabras por sección, enlaces e índice sin actualizar.

Por cada .xlsx escribe <nombre>.md con todas las hojas, fila por fila.

La paginación de Word no está en el XML: para ubicar un hallazgo se cita la sección y el párrafo [¶N], no la página.
"""
import os
import re
import sys
import zipfile
from collections import OrderedDict

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
q = lambda t: "{%s}%s" % (W, t)

TITULOS = {"ttulo1": 1, "ttulo2": 2, "ttulo3": 3, "ttulo4": 4, "heading1": 1, "heading2": 2, "heading3": 3,
           "heading4": 4, "titulo1": 1, "titulo2": 2, "titulo3": 3, "titulo4": 4}
IMG = {"zip": None, "dir": None, "sub": None, "lista": []}  # imágenes exportadas del documento en curso


def exportar_imagen(rid, rels):
    """Copia la imagen del paquete a <out>/<base>.img/ y devuelve la ruta relativa, o '' si no se puede."""
    destino = rels.get(rid or "", "")
    if not destino or IMG["zip"] is None:
        return ""
    interno = "word/" + destino.lstrip("/") if not destino.startswith("word/") else destino
    interno = os.path.normpath(interno).replace(os.sep, "/")
    try:
        datos = IMG["zip"].read(interno)
    except KeyError:
        return ""
    nombre = os.path.basename(interno)
    os.makedirs(os.path.join(IMG["dir"], IMG["sub"]), exist_ok=True)
    with open(os.path.join(IMG["dir"], IMG["sub"], nombre), "wb") as f:
        f.write(datos)
    return f"{IMG['sub']}/{nombre}"


TOC = re.compile(r"^(tdc|toc)\d*$|tabladeilustraciones|tableoffigures", re.I)


def leer_rels(z):
    rels = {}
    try:
        x = etree.fromstring(z.read("word/_rels/document.xml.rels"))
    except KeyError:
        return rels
    for r in x:
        rels[r.get("Id")] = r.get("Target")
    return rels


def estilo(p):
    ps = p.find(f"{q('pPr')}/{q('pStyle')}")
    return ps.get(q("val")) if ps is not None else ""


def texto_run(r, rels):
    out = []
    resaltado = r.find(f"{q('rPr')}/{q('highlight')}") is not None or \
        r.find(f"{q('rPr')}/{q('shd')}[@{q('fill')}='FFFF00']") is not None
    for e in r:
        if e.tag == q("t"):
            out.append(e.text or "")
        elif e.tag == q("tab"):
            out.append("\t")
        elif e.tag in (q("br"), q("cr")):
            out.append(" / ")
        elif e.tag == q("noBreakHyphen"):
            out.append("-")
        elif e.tag == q("drawing"):
            doc_pr = e.find(f".//{{{WP}}}docPr")
            nombre = (doc_pr.get("descr") or doc_pr.get("name")) if doc_pr is not None else "imagen"
            blip = e.find(f".//{{{A}}}blip")
            ruta = exportar_imagen(blip.get("{%s}embed" % R), rels) if blip is not None else ""
            out.append(f"[IMAGEN: {nombre} | archivo: {ruta}]" if ruta else f"[IMAGEN: {nombre}]")
            if ruta:
                IMG["lista"].append(ruta)
        elif e.tag == q("pict") or e.tag == q("object"):
            img = e.find(".//{urn:schemas-microsoft-com:vml}imagedata")
            ruta = exportar_imagen(img.get("{%s}id" % R), rels) if img is not None else ""
            out.append(f"[IMAGEN: {ruta}]" if ruta else "[IMAGEN o OBJETO]")
            if ruta:
                IMG["lista"].append(ruta)
    s = "".join(out)
    return f"=={s}==" if resaltado and s.strip() else s


def texto_parrafo(p, rels):
    # Recorrido ordenado de runs e hipervínculos (los campos TC y PAGEREF se omiten).
    def recorrer(nodo):
        out = []
        saltar = False
        for e in nodo:
            if e.tag == q("hyperlink"):
                t = "".join(texto_run(r, rels) for r in e.iter(q("r")))
                rid = e.get("{%s}id" % R)
                url = rels.get(rid, "") if rid else ("#" + (e.get(q("anchor")) or ""))
                out.append(f"[{t}]({url})" if t.strip() else "")
            elif e.tag == q("r"):
                fc = e.find(q("fldChar"))
                it = e.find(q("instrText"))
                if fc is not None:
                    tipo = fc.get(q("fldCharType"))
                    if tipo == "begin":
                        saltar = True
                    elif tipo == "separate":
                        saltar = False
                    elif tipo == "end":
                        saltar = False
                    continue
                if it is not None:
                    continue
                if not saltar:
                    out.append(texto_run(e, rels))
            elif e.tag in (q("ins"), q("smartTag"), q("customXml"), q("sdt"), q("sdtContent")):
                out.extend(recorrer(e))
            elif e.tag == q("del"):
                t = "".join((x.text or "") for x in e.iter(q("delText")))
                if t:
                    out.append(f"~~{t}~~")
        return out
    return "".join(recorrer(p)).strip()


def tabla_md(tbl, rels):
    filas = []
    for tr in tbl.findall(q("tr")):
        celdas = []
        for tc in tr.findall(q("tc")):
            ps = [texto_parrafo(p, rels) for p in tc.iter(q("p"))]
            celdas.append(" / ".join(x for x in ps if x).replace("|", "\\|"))
        filas.append(celdas)
    if not filas:
        return ""
    n = max(len(f) for f in filas)
    filas = [f + [""] * (n - len(f)) for f in filas]
    lineas = ["| " + " | ".join(filas[0]) + " |", "|" + "---|" * n]
    lineas += ["| " + " | ".join(f) + " |" for f in filas[1:]]
    return "\n".join(lineas)


def docx(path, out_dir):
    z = zipfile.ZipFile(path)
    rels = leer_rels(z)
    IMG.update(zip=z, dir=out_dir, sub=os.path.splitext(os.path.basename(path))[0] + ".img", lista=[])
    cuerpo = etree.fromstring(z.read("word/document.xml")).find(q("body"))
    md, chequeos = [], []
    n_par, n_tab = 0, 0
    secciones = OrderedDict()
    actual = "(antes del primer título)"
    secciones[actual] = 0
    ultimo_titulo = None
    toc_lineas = []
    marcadores, resaltados, rotulos, enlaces, vacios = [], [], [], [], []
    figuras, ultimo_rotulo = [], "(sin rótulo antes)"

    for e in cuerpo:
        if e.tag == q("p"):
            n_par += 1
            antes = len(IMG["lista"])
            st = estilo(e)
            t = texto_parrafo(e, rels)
            stl = st.lower()
            if TOC.search(stl):
                toc_lineas.append(t)
                continue
            if stl in TITULOS:
                nivel = TITULOS[stl]
                if ultimo_titulo is not None and ultimo_titulo[1] >= nivel:
                    vacios.append(ultimo_titulo[0])
                ultimo_titulo = (f"{t} [¶{n_par}]", nivel)
                ultimo_rotulo = f"(sin rótulo; bajo el título {t[:60]})"
                actual = f"{'#' * nivel} {t[:90]} [¶{n_par}]"
                secciones[actual] = 0
                md.append(f"\n{'#' * nivel} {t}  [¶{n_par}]\n")
                continue
            if len(IMG["lista"]) > antes:
                figuras.append([IMG["lista"][-1], n_par, ultimo_rotulo, None])
            if not t:
                continue
            ultimo_titulo = None
            secciones[actual] = secciones.get(actual, 0) + len(re.findall(r"\w+", t))
            etiqueta = f" ({st})" if st and stl not in ("normal", "prrafodelista", "listparagraph") else ""
            md.append(f"[¶{n_par}]{etiqueta} {t}\n")
            for m in re.finditer(r"==(.+?)==", t):
                resaltados.append(f"[¶{n_par}] {m.group(1)}")
            for m in re.finditer(r"\[(?!IMAGEN|¶)[^\]]{3,80}\](?!\()", t):
                marcadores.append(f"[¶{n_par}] {m.group(0)}")
            if re.match(r"^(Tabla|Figura)\s+\d+", t):
                rotulos.append(f"[¶{n_par}] {t[:120]}")
                ultimo_rotulo = f"[¶{n_par}] {t[:120]}"
            if figuras and figuras[-1][3] is None and figuras[-1][1] != n_par and n_par - figuras[-1][1] <= 3 and (t.startswith("Nota") or t.startswith("Fuente")):
                figuras[-1][3] = f"[¶{n_par}] {t[:160]}"
            for m in re.finditer(r"\[([^\]]+)\]\((http[^)]+)\)", t):
                enlaces.append(f"[¶{n_par}] {m.group(1)} -> {m.group(2)}")
        elif e.tag == q("tbl"):
            n_tab += 1
            ultimo_titulo = None
            md.append(f"\n[TABLA {n_tab}, después de ¶{n_par}]\n{tabla_md(e, rels)}\n")
            for p in e.iter(q("p")):
                t = texto_parrafo(p, rels)
                secciones[actual] = secciones.get(actual, 0) + len(re.findall(r"\w+", t))
                for m in re.finditer(r"==(.+?)==", t):
                    resaltados.append(f"[TABLA {n_tab}] {m.group(1)}")
        elif e.tag == q("sdt"):
            for p in e.iter(q("p")):
                t = texto_parrafo(p, rels)
                if t:
                    toc_lineas.append(t)

    comentarios = []
    if "word/comments.xml" in z.namelist():
        for c in etree.fromstring(z.read("word/comments.xml")).findall(q("comment")):
            comentarios.append(f"{c.get(q('author'))}: " + " ".join(texto_parrafo(p, rels) for p in c.iter(q("p"))))

    base = os.path.splitext(os.path.basename(path))[0]
    with open(os.path.join(out_dir, base + ".md"), "w", encoding="utf-8") as f:
        f.write(f"<!-- Extraído de {os.path.basename(path)}. [¶N] = número de párrafo del cuerpo. -->\n")
        f.write("".join(x if x.endswith("\n") else x + "\n" for x in md))
    with open(os.path.join(out_dir, base + ".chequeos.md"), "w", encoding="utf-8") as f:
        f.write(f"# Chequeos mecánicos de {os.path.basename(path)}\n\n")
        f.write(f"Párrafos: {n_par}. Tablas: {n_tab}.\n\n")
        f.write("## Índice y listas tal como están guardados (si no coinciden con los títulos, no se actualizaron)\n")
        f.write("\n".join(f"- {t}" for t in toc_lineas[:400]) or "(no hay)")
        f.write("\n\n## Títulos sin contenido debajo (antes del siguiente título del mismo nivel o superior)\n")
        f.write("\n".join(f"- {t}" for t in vacios) or "(ninguno)")
        f.write("\n\n## Texto resaltado\n" + ("\n".join(f"- {t}" for t in resaltados) or "(ninguno)"))
        f.write("\n\n## Posibles marcadores entre corchetes\n" + ("\n".join(f"- {t}" for t in marcadores) or "(ninguno)"))
        f.write("\n\n## Rótulos de tablas y figuras, en orden\n" + ("\n".join(f"- {t}" for t in rotulos) or "(ninguno)"))
        f.write("\n\n## Figuras e imágenes (archivo exportado, párrafo, último rótulo antes, nota o fuente después)\n")
        f.write("\n".join(f"- {a} [¶{n}] | rótulo: {r} | nota: {nt or '(ninguna)'}" for a, n, r, nt in figuras) or "(ninguna)")
        f.write("\n\n## Hipervínculos\n" + ("\n".join(f"- {t}" for t in enlaces) or "(ninguno)"))
        f.write("\n\n## Palabras por sección (cuerpo y tablas)\n")
        f.write("\n".join(f"- {k}: {v}" for k, v in secciones.items()))
        f.write("\n\n## Comentarios\n" + ("\n".join(f"- {c}" for c in comentarios) or "(ninguno)") + "\n")
    print("escrito:", os.path.join(out_dir, base + ".md"), "y .chequeos.md")


def xlsx(path, out_dir):
    import warnings
    warnings.filterwarnings("ignore")
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True)
    base = os.path.splitext(os.path.basename(path))[0]
    with open(os.path.join(out_dir, base + ".md"), "w", encoding="utf-8") as f:
        for ws in wb:
            f.write(f"## Hoja: {ws.title}\n\n")
            for fila in ws.iter_rows(values_only=True):
                v = [str(c).strip() for c in fila if c not in (None, "")]
                if v:
                    f.write(" | ".join(v) + "\n")
            f.write("\n")
    print("escrito:", os.path.join(out_dir, base + ".md"))


def main():
    args = sys.argv[1:]
    if "--out" not in args:
        sys.exit(__doc__)
    i = args.index("--out")
    out_dir = args[i + 1]
    archivos = args[:i] + args[i + 2:]
    os.makedirs(out_dir, exist_ok=True)
    for a in archivos:
        if a.lower().endswith(".docx"):
            docx(a, out_dir)
        elif a.lower().endswith(".xlsx"):
            xlsx(a, out_dir)
        else:
            print("se omite (no es .docx ni .xlsx):", a)


if __name__ == "__main__":
    main()
