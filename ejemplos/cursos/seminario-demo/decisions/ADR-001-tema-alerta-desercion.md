# ADR-001 — Tema: alerta temprana de deserción estudiantil con aprendizaje automático

- **Fecha**: 2027-03-15
- **Estado**: Aceptada
- **Curso**: seminario-demo
- **Autor(es)**: estudiante de la demo

*Decisión ficticia de la demo de cordada-ai.*

## Contexto

El sílabo pide una propuesta de investigación aplicada con un problema real de una organización (`docs/silabo-demo.md`, §1). La universidad del caso tiene una tasa de abandono alta en los primeros ciclos y detecta tarde a los estudiantes en riesgo.

## Decisión

Proponer un sistema de alerta temprana que estime el riesgo de deserción de cada estudiante con aprendizaje automático y explique los factores de ese riesgo a los tutores.

## Alternativas consideradas

- **Alerta temprana de deserción** (elegida): hay datos académicos disponibles y la literatura reciente es abundante.
- **Recomendador de tutorías**: interesante, pero depende de datos de tutorías que la universidad del caso no registra.
- **Chatbot de orientación**: no aborda la causa del problema, que es la detección tardía.

## Consecuencias

- **Positivas**: el tema permite preguntas claras sobre técnica, factores y validación.
- **Negativas**: hay que anonimizar los datos de los estudiantes antes de usarlos con cualquier herramienta de IA.
- **Impacto en otros artefactos**: las cadenas de búsqueda (`deliverables/busqueda/cadenas.json`) y las preguntas de investigación.

## Referencias

- `docs/silabo-demo.md`, §1 y §3.
