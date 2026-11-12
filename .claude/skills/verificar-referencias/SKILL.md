---
name: verificar-referencias
description: Verifica que las referencias bibliográficas existan y cumplan los criterios de fuentes del curso. Comprueba el DOI en Crossref y DataCite, el año (con la fecha de primera publicación en OpenAlex), que esté publicado en un volumen y no en prensa, que sea artículo de revista, la indexación y el cuartil en SCImago (CSV local), el acceso abierto y las retractaciones. Luego guía la revisión manual de si es un artículo de aporte o una revisión y de si la revista es depredadora. Actívalo cuando el usuario quiera validar, revisar o filtrar artículos, DOIs o una bibliografía; cuando pregunte si un paper "sirve", "cumple", "es Q1", "es muy antiguo" o "existe"; o cuando se agreguen fuentes encontradas con IA o búsqueda web. No lo uses para dar formato APA (eso es apa7).
---

# Verificar referencias

## Por qué existe

Los trabajos académicos piden fuentes con criterios estrictos, y revisarlas a mano una por una es lento y deja huecos. Además, los resúmenes de los buscadores y los modelos de lenguaje **inventan citas** con autores, revistas y volúmenes creíbles. Aquí nada se da por válido sin contrastarlo con una fuente primaria.

`scripts/verificar_referencias.py` resuelve lo comprobable. Lo que requiere criterio (aporte o revisión, revista depredadora) lo haces tú con los pasos de abajo. El usuario debe recibir un veredicto completo, no una lista de "revisar a mano".

## Criterios

Los **valores** salen de la sección "Criterios de fuentes" del `CLAUDE.md` del curso. Si el curso no los fija, pregunta al usuario o usa los valores por defecto del script y dilo en el veredicto.

| Criterio | Cómo se verifica | Parámetro |
|---|---|---|
| El artículo existe y la cita coincide (autores, año, volumen) | Crossref; si no está, doi.org y DataCite | — |
| Antigüedad máxima | Año en Crossref y **fecha de primera publicación** en OpenAlex. Si la publicación en línea es anterior al mínimo, se marca "?" | `--anios` (por defecto 5) |
| Publicado en volumen, no *in press* ni preprint | Crossref tiene volumen y número o páginas | — |
| Artículo de revista, no congreso ni capítulo | Tipo en Crossref (`journal-article`) | — |
| Revista indexada y cuartil (**mejor cuartil** entre sus categorías) | CSV de SCImago por ISSN | `--cuartiles-preferidos`, `--cuartiles-aceptados` |
| Acceso abierto, idioma, retractación | OpenAlex (informativo) | — |
| De aporte y no revisión | Señales automáticas + **lectura del abstract (tú)** | — |
| Revista no depredadora | **Revisión tuya** | — |

## Procedimiento

### 1. Reunir los DOIs

- DOIs sueltos o URLs `https://doi.org/...`.
- Un `.md` o `.txt` con referencias: el script lee la sección "Referencias" si existe, extrae los DOIs y compara el año y el volumen escritos con Crossref. Así detecta citas con datos cambiados.
- Títulos sin DOI: busca el DOI en Crossref (`https://api.crossref.org/works?query.bibliographic=<título>&rows=3`) y confírmalo con el usuario si el resultado es dudoso. **No adivines un DOI de memoria.**

### 2. Ejecutar el script

```bash
python3 .claude/skills/verificar-referencias/scripts/verificar_referencias.py \
  --refs <archivo>  [DOI ...] \
  --anios <N> --cuartiles-preferidos Q1,Q2 --cuartiles-aceptados Q1,Q2,Q3,Q4 \
  [--out reporte.md] [--json datos.json] [--widgets <carpeta>]
```

**CSV de SCImago**: el script lo busca en `--sjr`, en la variable `SJR_CSV`, en `docs/referencia/` del directorio actual y en `perfil/referencia/` de la raíz del workspace. Si no lo encuentra, pide al usuario que lo descargue (ver abajo). No intentes descargarlo tú: SCImago bloquea el acceso automático.

### 3. Completar lo que queda como "?"

**De aporte o revisión.** Lee el abstract que trae el reporte. Si viene cortado o vacío (pasa con Elsevier, que no lo comparte con Crossref ni OpenAlex), búscalo en este orden:
1. Semantic Scholar: `https://api.semanticscholar.org/graph/v1/paper/DOI:<doi>?fields=abstract`.
2. El repositorio institucional del autor (páginas Pure, sitio de la universidad), buscando el título entre comillas.
3. La página de la editorial.

Un abstract que sale del resumen de un buscador, y no de una página que lo muestre textual, no está verificado.

Clasifica cada artículo:
- **De aporte**: propone y **evalúa** algo propio, como un modelo, sistema, método, experimento o caso con resultados.
- **Revisión** (survey, revisión sistemática, metaanálisis, bibliometría): sintetiza trabajos ajenos. No cumple cuando el curso pide artículos de aporte, aunque sea Q1. Puede servir para encontrar artículos de aporte en sus referencias.
- **Artefacto de Design Science Research** (un framework o método construido y evaluado con expertos o en un caso): cuenta como aporte aunque la evaluación sea cualitativa.
- **Dudoso** (framework conceptual sin evaluación, artículo de opinión): márcalo como dudoso y explica por qué. No lo apruebes ni lo descartes en silencio.

**Revista depredadora.** Exigir indexación en SCImago descarta la mayoría, pero revisa con más cuidado los cuartiles bajos:
- **Revista secuestrada**: el DOI o la URL deben ser de la editorial que figura en SCImago. Retraction Watch mantiene un *Hijacked Journal Checker*.
- Señales de alerta: la editorial figura en listas conocidas de depredadoras (archivo de la lista de Beall), promete revisión en días o cobra de forma opaca.
- Estas señales son criterio general, no reglas del curso: preséntalas como alerta con su motivo.

**Referencias sin DOI** (informes, tesis, libros, webs): verifica que la URL abra el documento citado y que coincidan el título y el año. Aplica el criterio de antigüedad del curso para esas fuentes.

### 4. Entregar el veredicto

Una tabla corta: **Cumple / Cumple (no preferido) / No cumple / Dudoso** por referencia, con el motivo concreto de cada falla ("2019: anterior al mínimo", "revisión sistemática", "no indexada en SJR 2025", "DOI inexistente"). Además:
- qué hacer con cada falla: reemplazar, buscar la versión publicada de un preprint o mantenerla como fuente complementaria;
- la edición del CSV usada ("SJR 2025"): los cuartiles cambian cada año;
- **si una referencia que falla vino de una salida de IA** (búsqueda web, asistente, un borrador), agrégala a `deliverables/registro-errores-ia.md` del curso: "Cita inventada" si el DOI no existe o los datos no coinciden, "Criterio incumplido" si no cumple un criterio. Actualiza el conteo.

No reescribas las referencias en APA salvo que te lo pidan (skill `apa7`).

## Actualizar el CSV de SCImago

SCImago publica una edición al año. El usuario:
1. abre https://www.scimagojr.com/journalrank.php en su navegador y hace clic en **Download data**;
2. guarda el archivo como `perfil/referencia/scimagojr <año>.csv` (o en `docs/referencia/` del curso).

El script toma el de año más alto. Si una revista no aparece por ISSN, búscala por título (columna `Title`). Para tener evidencia del cuartil, `--widgets` deja la URL del widget oficial (`journal_img.php?id=<Sourceid>`). SCImago suele bloquear su descarga automática: el usuario la abre en su navegador y guarda la imagen.

## Límites conocidos

- **Crossref sin volumen**: los artículos recién publicados tardan semanas en mostrarlo. Si la web de la revista ya lo muestra, prevalece la web.
- **Crossref no distingue revisiones**: también figuran como `journal-article`. La clasificación final siempre es tuya, leyendo el abstract.
- **OpenAlex pone el 1 de enero** cuando solo conoce el año. Si el artículo está en el límite del periodo, confirma la fecha en la editorial.
- **Retractaciones**: solo se detectan si OpenAlex las marca. Revisa la página de la editorial si el artículo es central.
