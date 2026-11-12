---
name: informe-articulo
description: Redacta el informe de revisión de un artículo científico a partir de su texto completo, con la página de cada dato. Baja el PDF abierto (OpenAlex) o usa el que pase el usuario, extrae el texto con páginas, escribe las secciones que pida la plantilla del curso (por defecto problema, importancia, aporte, proceso, resultados, síntesis por pregunta, críticas y referencias), agrega una guía de defensa para quien lo presenta y registra el uso de IA. Actívalo cuando el usuario pida "el informe del artículo N", "la ficha del paper", "analiza este artículo para el estado del arte" o preparar la defensa de un artículo. No lo uses para buscar o seleccionar artículos (buscar-articulos) ni para validar criterios de fuentes (verificar-referencias).
---

# Informe de revisión de un artículo

## Por qué existe

En una revisión de literatura, cada artículo suele llevar un informe, y quien lo firma tiene que poder defenderlo: el docente puede preguntar al azar. Por eso el informe tiene que ser **fiel al artículo y verificable**. Cada dato lleva su página, el borrador se marca como tal y el uso de IA queda registrado.

## Antes de empezar

En el `CLAUDE.md` del curso:
- **La plantilla del informe** y lo que pide cada sección. Si el curso tiene su propia estructura, esa manda sobre la de este skill.
- **Las preguntas de investigación** y el **contexto del proyecto** (tema, alcance, objetivos), para la síntesis y las críticas.
- **Lo que permite el docente** sobre el uso de IA y qué hay que declarar.

## Procedimiento

### 1. Obtener el texto completo

```bash
python3 .claude/skills/informe-articulo/scripts/obtener_texto.py <DOI> \
  --out courses/<slug>/deliverables/informes/articulo-NN [--pdf archivo.pdf]
```

El script baja el PDF abierto que declara OpenAlex y escribe `texto.txt`, con `=== Página N ===` antes de cada página, y `meta.json` (autores, revista, fecha de publicación). Algunas editoriales (Wiley, IEEE Xplore) bloquean la descarga automática aunque el artículo sea abierto: el usuario baja el PDF y se pasa con `--pdf`. Requiere `pdftotext` (poppler).

**No se redacta un informe desde el resumen.** Si no hay texto completo, se detiene aquí.

### 2. Leer el artículo completo

Lee `texto.txt` entero, no solo el resumen y las conclusiones. Anota por sección los datos que vas a usar, con su página. Sin página, el dato no entra.

### 3. Redactar

Escribe `informe-articulo-NN.md` en la carpeta del artículo. Estilo: un párrafo por sección (salvo Proceso, en lista numerada), parafraseado; las citas textuales van con comillas y página; el artículo se cita en la norma del perfil.

**Estructura por defecto** (si el curso no fija otra):

| Sección | Qué va |
|---|---|
| Ficha | Título original (y su traducción), autores, revista, fecha de primera publicación, cuartil (mejor cuartil y edición del SJR), tipo de documento |
| 1. Problema | La situación que abordan los autores, y si se parece al problema del proyecto |
| 2. Importancia | Por qué importa, con la evidencia y las citas que usan los autores |
| 3. Aporte | La contribución principal (modelo, sistema, método), sus componentes y su novedad |
| 4. Proceso | Pasos de construcción y **cómo validaron**: datos, método, métricas |
| 5. Resultados y conclusiones | Cifras de la validación (tabla con nota "Adaptado de…"), conclusiones, limitaciones y trabajo futuro según los autores |
| 6. Síntesis | Qué responde para cada pregunta de investigación, con fragmento y página |
| 7. Críticas | Incoherencias, limitaciones para aplicarlo al proyecto, vacíos y **qué se puede reutilizar** |
| 8. Referencias | El artículo y las fuentes citadas en el informe |

**Críticas**: cada una dice qué falla, con qué evidencia (página o tabla), por qué importa para este proyecto y qué se hace con eso. Las críticas genéricas ("la muestra es pequeña") sin consecuencia para el proyecto no sirven.

### 4. Guía de defensa (no va en el entregable)

Al final del `.md`, en "Notas para quien lo presenta":
- **5 preguntas probables** sobre el artículo (problema, aporte, validación, resultado principal, utilidad para el proyecto), con una respuesta de 2 a 3 líneas y su página;
- los **términos técnicos**, con una definición de una línea;
- el recordatorio: **hay que leer el artículo completo**; el borrador no reemplaza esa lectura.

### 5. Registrar el uso de IA

En `courses/<slug>/deliverables/registro-uso-ia.md` agrega una fila con:
- fecha, integrante y herramienta;
- tarea (extracción, borrador, guía de defensa);
- instrucción resumida;
- estado de la revisión humana.

Además:
- si en la revisión aparece un dato del borrador que no está en el artículo, o tiene la página equivocada, regístralo en `registro-errores-ia.md` como "Dato sin respaldo";
- cuando el usuario confirme o descarte el artículo después de leerlo, registra la decisión en `decisiones-humanas.json` con la etapa "texto completo".

### 6. Entregar

En el chat: la ruta del informe, lo que no se pudo verificar y lo que el usuario tiene que revisar sí o sí antes de usarlo. Los informes se pegan a mano en el Word del curso (`AGENTS.md`, sección 6).
