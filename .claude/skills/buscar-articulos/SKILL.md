---
name: buscar-articulos
description: Revisión de literatura reproducible. Ejecuta las cadenas de búsqueda en Scopus (API oficial con la key del usuario) o procesa exportaciones CSV de Scopus y de Web of Science; elimina duplicados, completa resúmenes desde fuentes abiertas, aplica los criterios de inclusión y exclusión automatizables, cuenta las etapas de PRISMA 2020 y prepara el cribado asistido por título y resumen, ordenado por afinidad con las preguntas de investigación. Actívalo cuando el usuario quiera correr o ajustar cadenas de búsqueda, armar el estado del arte o un marco de antecedentes, obtener números para un diagrama PRISMA, o cuando pase un CSV de Scopus o un savedrecs de WoS. No lo uses para validar una lista ya elegida (eso es verificar-referencias) ni para buscar normativa, cifras o libros.
---

# Buscar artículos para una revisión de literatura

## Por qué existe

Un estado del arte se defiende mostrando el proceso: bases, cadenas, fechas, conteos y motivos de exclusión. Hacerlo a mano en la web es lento, y las búsquedas con IA no sirven porque no se pueden reproducir e inventan citas.

El trabajo se reparte así:
- **El script** hace lo mecánico: consulta la API, pagina, elimina duplicados, completa resúmenes, aplica los criterios verificables por máquina y cuenta las etapas de PRISMA.
- **Tú** haces el cribado por título y resumen, con motivos explícitos.
- **El usuario** lee y decide. Tu cribado es una recomendación argumentada; la selección es responsabilidad de quien la defiende.

## Qué necesitas

| Elemento | Dónde |
|---|---|
| Cadenas de búsqueda (fuente única) | `courses/<slug>/deliverables/busqueda/cadenas.json`, con el formato de abajo |
| API key de Elsevier (Scopus) | `~/.config/elsevier/apikey` (permisos 600) o la variable `ELSEVIER_API_KEY`. Se pide en https://dev.elsevier.com con acceso institucional. **Nunca imprimirla ni copiarla al chat.** Sin key, usa el plan B (CSV). |
| CSV de SCImago | El mismo que usa `verificar-referencias` |
| Criterios del curso | Sección "Criterios de fuentes" del `CLAUDE.md` del curso |

**Formato de `cadenas.json`**: las claves que empiezan con `_` son metadatos. `_preguntas` da la afinidad con las preguntas de investigación (opcional) y `_historial` documenta las iteraciones de las cadenas.

```json
{
  "_preguntas": {
    "P1": {"categoria": "Problema", "palabras": ["student dropout", "attrition"]},
    "P2": {"categoria": "Técnica", "palabras": ["machine learning", "random forest"]}
  },
  "_historial": [
    {"fecha": "2027-03-10", "cadena": "C1", "antes": "...", "despues": "...", "motivo": "..."}
  ],
  "C1": {"preguntas": "P1, P2", "query": "TITLE-ABS-KEY((\"student dropout\") AND (\"machine learning\"))"}
}
```

## Procedimiento

### 1. Ejecutar

```bash
python3 .claude/skills/buscar-articulos/scripts/buscar_articulos.py \
  --cadenas courses/<slug>/deliverables/busqueda/cadenas.json \
  --out courses/<slug>/deliverables/busqueda/$(date +%F) \
  --anios <N> --cuartiles-preferidos Q1,Q2 --idiomas en,es
```

Opciones:
- `--solo C2 C3`: correr solo algunas cadenas.
- `--csv C1=export.csv` o `--wos C1=savedrecs.txt`: **plan B** sin API. El usuario exporta desde la web con *Citation information* y *Abstract & keywords*. Con exportaciones, las preguntas se pasan con `--preguntas cadenas.json`.
- `--anios N`: años hacia atrás, incluido el actual (4 = el actual y los 3 anteriores).

Variables opcionales: `SEMANTIC_SCHOLAR_API_KEY` (evita errores 429) y `OPENALEX_MAILTO`. Con la caché (`.cache_resumenes.json`), una segunda corrida tarda menos.

**Salida** en `--out`:
- `cadenas-resultados.md`: conteo por cadena y fecha.
- `prisma.md`: identificados, duplicados, excluidos automáticos por criterio y los que pasan al cribado.
- `candidatos.md`: cada candidato con su ficha y **resumen completo**, ordenado por afinidad.
- `excluidos.md`: excluidos automáticamente, con su motivo.
- `resultados.json`: todo, para análisis posteriores.

**Criterios automáticos** (los códigos aparecen en los motivos):

| Código | Criterio |
|---|---|
| CI2 | Publicado fuera del periodo (`--anios`) |
| CE1 | Revisión o survey (por título o tipo) |
| CE2 | No es artículo de revista |
| CE3 | Sin volumen asignado (posible en prensa) |
| CE4 | Revista sin cuartil en el CSV de SCImago |
| CI4 | Idioma fuera de `--idiomas` |

Si el curso define otros criterios, documenta la correspondencia en el `CLAUDE.md` del curso o en una ADR.

### 2. Revisar la salud de las cadenas antes de cribar

- **Estructura**: una cadena útil combina bloques con AND, por ejemplo `(aporte) AND (problema) AND (técnica) AND (contexto)`. Si el docente fija una fórmula, esa manda.
- **Más de ~500 resultados**, o comodines que capturan otras cosas (`tax*` captura *taxonomy*): hay que acotarla. Prueba el conteo de la variante y muestra 10 a 25 títulos de muestra para juzgar el ruido.
- **Menos de ~20**: probablemente es demasiado estrecha.
- **Prueba de recuperación antes de cambiar una cadena**: arma un conjunto de control con los DOI "incluir" y "dudoso" de la corrida anterior y mide cuántos recupera la variante. Una cadena nueva no debe perder ningún "incluir" sin una razón explícita.
- **No cambies una cadena en silencio**: actualiza `cadenas.json`, agrega la línea en `_historial` (antes, después y motivo) y avisa al usuario. Esas iteraciones se documentan en la conducción de la revisión.

### 3. Cribar en dos pasadas (tu parte)

**Pasada 1, por título.** Excluye solo lo que está **claramente** fuera del tema. Ante la duda, pasa a la pasada 2.

**Pasada 2, por resumen.** Para cada sobreviviente:
- **Incluir**: artículo de aporte que propone y valida una solución, modelo o técnica, y responde una o más preguntas.
- **Dudoso**: relevante pero con algo por confirmar, como una validación débil, un cuartil no preferido o un dominio vecino.
- **Excluir**: con el criterio concreto.

Escribe motivos que se puedan auditar en segundos. "No relevante" no sirve; "estudia la evasión a nivel país con econometría, sin sistema ni modelo aplicable" sí.

- **Sin resumen**: si el título es prometedor, márcalo "Leer en la base". No lo excluyas por falta de resumen.
- **Resumen pobre**: lee la introducción y las conclusiones antes de decidir.
- **Publicado en línea antes del periodo**: trátalo como dudoso y confírmalo con `verificar-referencias`.

**Dónde se guarda:** en la carpeta de la corrida, `.cribado_p1.json` (`{"pasada1_excluidos": {n: motivo}}`) y `.cribado_p2.json` (`{"pasada2": {n: [decisión, motivo, "P1,P2", categoría]}}`). La clave es el número de candidato; `.orden_candidatos.json` traduce número a DOI. **En una corrida nueva, hereda por DOI** las decisiones de la anterior y lee solo los candidatos nuevos.

Estos JSON guardan **solo la recomendación de la IA**. La decisión humana va aparte (paso 5), para poder medir cuánto coinciden.

Escribe `cribado.md` con la tabla (N.º, título abreviado, decisión de la IA, motivo, preguntas, categoría, decisión humana) y los conteos para PRISMA. Si el curso pide un número fijo de artículos, propón la selección con un **balance por pregunta**, una **matriz pregunta → artículos** y **suplentes**, y valídala con `verificar-referencias` **antes** de proponerla.

### 4. Entregar

Resume en el chat: conteos de PRISMA, cadenas ajustadas, la selección propuesta y los enlaces DOI. Recuerda que la decisión es del usuario y que los "Leer en la base" requieren su acceso institucional.

### 5. Después de que el usuario decida

- **Registra cada decisión humana** en `courses/<slug>/deliverables/decisiones-humanas.json`: la clave es el DOI en minúsculas, y cada entrada lleva decisión, etapa, recomendación de la IA, motivo, quién y fecha. No borres entradas. Si la decisión contradice a la IA, pide el motivo en una línea: es el dato más valioso.
- Si `verificar-referencias` descarta un candidato que la IA recomendó incluir, regístralo en `deliverables/registro-errores-ia.md` con el tipo "Criterio incumplido".
- Deja los números listos para el diagrama PRISMA.

## Límites

- La afinidad es un conteo de palabras clave para **ordenar la lectura**, no para decidir.
- **Solo se usa la API oficial.** No automatices la web de Scopus ni el proxy de la universidad: los términos de Elsevier prohíben las descargas automatizadas y el acceso institucional podría bloquearse.
- WoS no tiene API con una key de Elsevier. Solo se procesan exportaciones manuales (`--wos`): verifica las columnas la primera vez.
- Elsevier no expone resúmenes por vías abiertas: esos se leen en Scopus con el acceso del usuario.
