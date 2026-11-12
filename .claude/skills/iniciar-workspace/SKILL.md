---
name: iniciar-workspace
description: Configura el workspace la primera vez que se usa. Pregunta la universidad, las normas académicas (norma de citación, guía de la biblioteca, acreditación, política de IA) y la forma de trabajo (individual o en equipo, git, cierre de sesión), y guarda todo en perfil/perfil.md. Ofrece la UPC como universidad de ejemplo e instala un curso de demostración. Actívalo siempre que no exista perfil/perfil.md, cuando el usuario diga "configura el workspace", "empecemos", "quiero ver la demo", "cambia mi universidad" o "pasemos a modo equipo".
---

# Iniciar el workspace

## Por qué existe

Las reglas de un curso dependen de su universidad: la guía de citación de la biblioteca, el marco de competencias, la política de uso de IA. Sin ese contexto, el agente aplicaría el estándar a ciegas o, peor, inventaría reglas. Este skill fija la capa institucional una sola vez (`AGENTS.md`, sección 1: curso > institución > estándar).

## Procedimiento

### 1. Saludar y ofrecer dos caminos

Una sola pregunta corta:

> Para empezar necesito saber dónde estudias. ¿Cómo se llama tu universidad?
> Si solo quieres ver cómo funciona, responde **"demo"** y uso la UPC (Universidad Peruana de Ciencias Aplicadas) como ejemplo, con un curso ficticio.

Si responde "demo", salta al paso 5.

### 2. Recoger el perfil

Haz las preguntas **en un solo mensaje**, con valores por defecto para que el usuario pueda responder rápido:

1. **Universidad**: nombre completo y sigla. *(ya respondida)*
2. **País e idioma de trabajo** (por defecto, el idioma de la conversación).
3. **Nivel y carrera**: pregrado, posgrado o ejecutivo; nombre de la carrera.
4. **Norma de citación**: por defecto APA 7. ¿Tu biblioteca tiene una guía propia? Si sí, la URL.
5. **Acreditación o marco de competencias** (por ejemplo, ABET), si los cursos lo piden. Por defecto, ninguno.
6. **Política de uso de IA** de la universidad, si existe (URL o resumen).
7. **Forma de trabajo**:
   - ¿Trabajas solo o en equipo? En equipo, nombres de los integrantes y su `git config user.name`.
   - ¿Usas git? (no / local / con repositorio remoto). En equipo, se requiere remoto.
   - Al cerrar sesión, ¿quieres confirmar el plan antes de escribir, o que el agente escriba directo e informe al final?
   - ¿Qué agentes usas? (Claude Code, Codex, Cursor…)

**No investigues ni completes por tu cuenta** lo que el usuario no respondió: deja "no indicada". Si da una URL de la guía de la biblioteca, puedes leerla después, con su permiso, para registrar las diferencias con el estándar (paso 4).

### 3. Escribir `perfil/perfil.md`

Copia `shared/templates/perfil.md` a `perfil/perfil.md` y llénalo con las respuestas. Muéstraselo al usuario en el chat, de forma resumida, antes de seguir.

### 4. Ajustes que dependen del perfil

- **Modo equipo**:
  - comprueba que el workspace sea un repositorio git con remoto (`git remote -v`); si no lo es, explica cómo crearlo y no lo crees sin permiso;
  - recuerda que cada integrante debe tener su `git config user.name` igual al de la tabla.
- **Guía de citación propia**: si el usuario dio la URL y acepta, léela y crea `perfil/citacion-local.md` solo con **las diferencias** respecto del estándar, cada una con su fuente (URL y sección). Si no puedes leerla, deja el archivo con un aviso de "pendiente".
- **Transcripciones de los agentes**: recomienda agregar `"cleanupPeriodDays": 3650` a `~/.claude/settings.json`, porque Claude Code borra las sesiones a los 30 días y son evidencia del uso de IA. Pide permiso antes de editar ese archivo, porque está fuera del workspace.
- **Privacidad**: recuerda en una línea revisar la configuración de entrenamiento con conversaciones de la cuenta del proveedor de IA.

### 5. Demo con la UPC

Si el usuario pidió la demo:
1. Copia `perfiles-ejemplo/upc/perfil.md` a `perfil/perfil.md` y `perfiles-ejemplo/upc/citacion-local.md` a `perfil/citacion-local.md`.
2. Copia `ejemplos/cursos/seminario-demo/` a `courses/seminario-demo/` y agrega su fila al índice de `CLAUDE.md`.
3. Explica en tres líneas qué hay en la demo y propón algo para probar, por ejemplo:
   - "para el curso de seminario demo, ¿qué falta para el próximo entregable?"
   - "verifica las referencias de `courses/seminario-demo/deliverables/referencias.md`"
   - "cierra sesión"
4. Aclara que la demo es ficticia: el curso, el docente y las reglas son inventados. La UPC aparece solo como ejemplo de perfil institucional, con información pública.

Para salir de la demo: borrar `perfil/perfil.md` y `perfil/citacion-local.md`, y volver a correr este skill. Pregunta antes de borrar `courses/seminario-demo/`.

### 6. Siguiente paso

Termina proponiendo crear el primer curso con `agregar-curso`.

## Cambiar el perfil después

Si el usuario dice "cambia mi universidad", "pasemos a modo equipo" o algo equivalente, edita solo los campos afectados de `perfil/perfil.md` y repite el paso 4 para lo que cambió. Al pasar de individual a equipo, renombra cada `JOURNAL.md` como `JOURNAL-<integrante>.md` (sin tocar las entradas) y agrega al STATE de cada curso una sección "Falta — <integrante>" por persona.

## Reglas

- No inventes datos de la universidad. Lo que no sepas, queda como "no indicada".
- `perfil/perfil.md` es del usuario: no lo sobrescribas entero si ya existe; edita campos.
- La UPC se usa solo como ejemplo. No sugieras que el proyecto está afiliado a ella.
