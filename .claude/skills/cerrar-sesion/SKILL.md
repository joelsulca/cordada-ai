---
name: cerrar-sesion
description: Cierra la sesión de trabajo y persiste la memoria del curso. Actualiza STATE.md, agrega una entrada al JOURNAL (uno por curso en modo individual, uno por integrante en modo equipo), registra los aprendizajes del usuario, propone ADR para las decisiones de largo plazo y, si el workspace usa git, hace commit (y push en modo equipo). Según el perfil, confirma antes de escribir o escribe directo e informa al final. Actívalo cuando el usuario diga "cierra sesión", "actualiza el estado", "guarda lo hecho", "termina por hoy", "guardar progreso" o algo equivalente.
---

# Cerrar sesión y persistir la memoria

## Antes de empezar

Lee en `perfil/perfil.md` tres campos:

| Campo | Efecto |
|---|---|
| **modo**: individual / equipo | Qué JOURNAL se escribe y si el STATE tiene secciones por persona |
| **git**: no / local / remoto | Si se hace commit y push |
| **cierre**: confirmar / directo | Si se muestra el plan antes de escribir |

## Procedimiento

### 1. Identificar quién y qué

- **Curso**: el que se trabajó en la sesión, el que indicó el usuario o el del directorio actual. Si fueron varios, aplica el flujo a cada uno. Si hay ambigüedad, pregunta con `cierre: confirmar`, o elige el curso con más archivos tocados y dilo con `cierre: directo`.
- **Integrante** (solo en modo equipo): `git config user.name` → tabla de integrantes del perfil. Si no aparece, pregunta: sin eso no se sabe en qué JOURNAL escribir.

### 2. Traer cambios (modo equipo)

`git pull --rebase` antes de preparar nada, para no pisar lo que subió otro integrante. Si hay cambios locales que lo impiden: `git stash`, pull y `git stash pop`. Los conflictos se resuelven conservando los aportes de ambos.

### 3. Preparar los cambios

**A) `STATE.md`**:
- **Individual**: reescríbelo con el estado actual: Hito actual, Progreso (listo y falta), Decisiones vivas, Próximos pasos y Bloqueadores.
- **Equipo**:
  - reescribe solo la sección "Falta — <integrante>" de quien cierra;
  - en las secciones comunes, edita solo las líneas que cambiaron;
  - **no toques la sección de otro integrante**: si algo le afecta, anótalo en Próximos pasos o Bloqueadores con su nombre.

**B) Entrada nueva en el JOURNAL** (`JOURNAL.md` en modo individual, `JOURNAL-<integrante>.md` en equipo), al final del archivo:

```markdown
## AAAA-MM-DD — <título breve de la sesión>

**Trabajado**:
- <ítem>

**Archivos tocados**:
- `<ruta>` — <qué cambió>

**Aprendizajes**: (opcional)
- <qué aprendió el usuario>: <cómo lo aprendió> → <dónde lo aplicó>

**Notas**: (opcional) <lo que conviene recordar>
```

**Sobre "Aprendizajes"**: son evidencia de las competencias del usuario. Muchas acreditaciones las piden; por ejemplo, ABET SO7 habla de "adquirir y aplicar nuevos conocimientos con estrategias de aprendizaje apropiadas".
- Registra solo lo que el usuario **aprendió en la sesión**, con evidencia en la conversación: una herramienta, un método, una regla del curso o un error que aprendió a detectar. No registres lo que el agente sabía y solo aplicó.
- Con `cierre: confirmar`, propónlas como borrador para que el usuario las confirme o las reescriba. Con `cierre: directo`, márcalas con "*(redactado por el agente; reescríbelo en una entrada nueva si no coincide)*".
- Si no hubo nada nuevo, omite el campo.

**C) Registros de IA**: si en la sesión se detectó un error de la IA, o una persona decidió distinto de lo que recomendó la IA, comprueba que esté en `deliverables/registro-errores-ia.md` o en `deliverables/decisiones-humanas.json` (`AGENTS.md`, sección 7). Si falta, agrégalo.

**D) ADR**: si en la sesión se tomó una decisión que aplica al curso o al proyecto entero, que tiene alternativas descartadas o que se citará en la defensa, prepara una ADR con `shared/templates/ADR-template.md`.
- Numérala después de la más alta de `courses/<slug>/decisions/`. En modo equipo, numérala después del pull.
- Créala con estado **Propuesta**.
- Agrégala al índice `decisions/README.md`.

### 4. Confirmar (solo con `cierre: confirmar`)

Muestra el plan antes de escribir: archivos, resumen de la entrada del JOURNAL, aprendizajes propuestos, ADR y commit. Espera la confirmación. Con `cierre: directo`, pasa al paso 5.

### 5. Escribir y sincronizar

1. Escribe en este orden: STATE → JOURNAL → registros → ADR.
2. Con git:
   - `git add` solo de los archivos de la sesión (revisa `git status`; no incluyas temporales);
   - `git commit` con un mensaje corto que lleve el curso como prefijo (`gerencia: informe del caso 2`).
3. Con remoto: `git push`. Si se rechaza, `git pull --rebase` y otra vez push. **Nunca `--force`.**

### 6. Informar

Un mensaje corto: qué archivos se escribieron, las ADR propuestas (en equipo, que el otro integrante las revise), los aprendizajes registrados y el commit. Si algo quedó anotado para otro integrante, dilo.

## Cuándo detenerse

- **Conflicto de git que no se resuelve conservando ambos aportes** (por ejemplo, dos versiones de un `.docx`): haz commit local de lo demás, no hagas push e informa qué archivo quedó en conflicto.
- **El usuario dijo antes, en la misma sesión, "no subas" o "no crees la ADR"**: respétalo.
- **No se puede identificar al integrante** en modo equipo: pregunta.

## Reglas duras

- **Los JOURNAL son append-only**: no se borran ni se editan entradas previas. En equipo, nadie escribe en el JOURNAL de otro.
- **Las ADR no se sobrescriben.** Si una decisión se revierte, la anterior se marca "Superseded by ADR-XXX" y se crea una nueva.
- **Nunca `git push --force`.**
