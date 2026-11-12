# Perfil del workspace

*Creado por `iniciar-workspace` el <AAAA-MM-DD>. Se puede editar a mano; si cambia algo, avisa al agente.*

## Institución

| Campo | Valor |
|---|---|
| Universidad | <NOMBRE COMPLETO> (<SIGLA>) |
| País | <PAÍS> |
| Idioma de trabajo | <es / en / …> |
| Nivel | <pregrado / posgrado / ejecutivo / otro> |
| Carrera o programa | <CARRERA> |

## Normas académicas

| Campo | Valor |
|---|---|
| Norma de citación | <APA 7 / IEEE / Vancouver / Chicago / otra> |
| Guía de la biblioteca | <URL o "no indicada"> |
| Diferencias locales con la norma | <`perfil/citacion-local.md` o "ninguna registrada"> |
| Acreditación o marco de competencias | <ABET, competencias propias, "ninguno"> |
| Política de uso de IA de la universidad | <URL, resumen o "no indicada"> |

> Las diferencias de la guía de la universidad con el estándar prevalecen sobre el estándar (`AGENTS.md`, sección 1). Regístralas con su fuente en `perfil/citacion-local.md`.

## Forma de trabajo

| Campo | Valor |
|---|---|
| Modo | <individual / equipo> |
| git | <no / local / remoto> |
| Cierre de sesión | <confirmar / directo> |
| Agentes que se usan | <Claude Code, Codex, …> |

`cierre: confirmar` muestra el plan antes de escribir. `cierre: directo` escribe, hace commit (y push, si hay remoto) e informa al final.

## Integrantes (solo en modo equipo)

| Integrante | `git config user.name` | JOURNAL |
|---|---|---|
| <Nombre> | `<usuario-git>` | `JOURNAL-<nombre>.md` |
