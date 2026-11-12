# Decisiones — <CURSO_NOMBRE>

Registro de decisiones de largo plazo del curso (ADR, *Architecture Decision Records*).

## Cuándo crear una ADR

Cuando la decisión:
- aplica al curso o al proyecto entero, no solo a la tarea del día;
- tiene alternativas descartadas que vale la pena recordar;
- se citará después en el documento final, en un examen o en la defensa.

Las decisiones tácticas del día a día van en `STATE.md` y en el JOURNAL.

## Plantilla

`shared/templates/ADR-template.md` (raíz del workspace). Nombre del archivo: `ADR-XXX-titulo-en-kebab-case.md`, con número secuencial de tres dígitos.

## Índice

| # | Título | Estado | Fecha |
|---|---|---|---|

## Reglas

- Las ADR **no se sobrescriben**. Si una decisión se revierte, la anterior se marca "Superseded by ADR-YYY" y se crea una nueva.
- Estados válidos: `Propuesta` | `Aceptada` | `Rechazada` | `Superseded by ADR-YYY`.
