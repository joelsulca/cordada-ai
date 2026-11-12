@AGENTS.md

# CLAUDE.md — cordada-ai

Este archivo extiende `AGENTS.md` con lo específico de Claude Code. Otros agentes leen `AGENTS.md` directamente.

## Perfil

El perfil de la universidad y la forma de trabajo están en `perfil/perfil.md`. **Si no existe, ejecuta el skill `iniciar-workspace` antes de cualquier otra cosa** (`AGENTS.md`, sección 0).

## Índice de cursos

Cada curso vive en `courses/<slug>/`. Cuando el usuario diga "para el curso de X…", ubícalo con la columna de keywords.

| Slug | Curso | Ciclo | Docente | Estado | Keywords |
|---|---|---|---|---|---|

*(El skill `agregar-curso` agrega una fila por curso.)*

## Protocolo al iniciar una sesión

1. Si no existe `perfil/perfil.md`: skill `iniciar-workspace`.
2. En modo equipo: identifica al integrante (`git config user.name` → tabla del perfil) y corre `git pull --rebase`.
3. Identifica el curso (`AGENTS.md`, sección 3).
4. Lee el `CLAUDE.md` y el `STATE.md` del curso, el índice `decisions/README.md` y la última entrada del JOURNAL.
5. Procede con el pedido.

## Reglas específicas de Claude Code

- **Abre Claude Code desde la raíz del workspace.** La memoria personal de Claude Code se asocia a la carpeta desde la que se abre.
- **Cierre de sesión bajo demanda**: el usuario decide cuándo cerrar ("cierra sesión", "guarda lo hecho"). Si el perfil dice `cierre: directo`, el cierre escribe sin pedir confirmación.
- **Confirma antes de escribir archivos importantes**: antes de modificar `docs/`, borrar entregables, crear ADR o hacer push. La excepción es `cierre: directo`.
- **Los skills se activan solos** por su descripción. No hace falta invocarlos con `/nombre`.
- **Transcripciones**: `iniciar-workspace` recomienda `"cleanupPeriodDays": 3650` en `~/.claude/settings.json`, porque son evidencia del uso de IA.
