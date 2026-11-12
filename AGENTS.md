# AGENTS.md — Reglas de cordada-ai

Este workspace organiza tus cursos para trabajar con agentes de IA (Claude Code, Codex, Cursor, Copilot, Cline u otros) con **memoria persistente por curso**, **reglas con fuente** y **evidencia del uso de IA**. Estas reglas valen para cualquier agente. Está optimizado para Claude Code, que carga solo los `CLAUDE.md` y activa los skills por su descripción. Con otros agentes funciona igual si siguen este archivo: los `CLAUDE.md` de cada curso y los `SKILL.md` se leen explícitamente (secciones 9 y 12).

## 0. Primer uso: el perfil

**Si no existe `perfil/perfil.md`, no hagas nada más: ejecuta el skill `iniciar-workspace`** (`.claude/skills/iniciar-workspace/SKILL.md`). Ese skill pregunta la universidad, las normas académicas y la forma de trabajo, y guarda las respuestas en `perfil/perfil.md`. Todo lo demás depende de ese archivo.

Si el usuario solo quiere ver una demo, `iniciar-workspace` ofrece la UPC como universidad de ejemplo e instala un curso ficticio.

## 1. Precedencia de reglas

Cuando dos reglas chocan, gana la más específica:

1. **El curso**: reglas del docente, con su fuente, en `courses/<slug>/CLAUDE.md`.
2. **La institución**: guías y normas de la universidad, en `perfil/perfil.md` y sus anexos.
3. **El estándar**: APA 7, ISO, PMBOK, UML y similares.

Se puede notar la divergencia si aporta claridad, pero no se "corrige" al docente ni a la institución.

## 2. Sourcing discipline (no negociable)

- Distingue siempre qué viene **literal del material del curso** (rúbricas, diapositivas, enunciados, guías del docente, transcripciones) y qué es **inferencia** propia.
- Al citar algo del material, indica la fuente concreta: archivo y sección, página o minuto.
- Si no sabes si algo está en el material o lo estás asumiendo, **dilo** antes de responder.
- No inventes convenciones del docente. Si el usuario menciona una regla que no está en el `CLAUDE.md` del curso, pregunta antes de aplicarla y propón agregarla con su fuente.
- **Nunca cites de memoria.** Toda referencia bibliográfica que propongas se verifica (DOI en Crossref, documento oficial) antes de usarla: los resúmenes de buscadores y los modelos de lenguaje inventan citas con apariencia creíble. Usa el skill `verificar-referencias`.

## 3. Identificación del curso

- Si el mensaje empieza con "para el curso de <X>…" o una variante equivalente, ese curso gana sobre cualquier otro contexto. Ubícalo con la columna de keywords del índice de `CLAUDE.md`.
- Sin prefijo, usa el curso del directorio actual (`courses/<slug>/`). Si se trabaja desde la raíz y hay un solo curso activo, usa ese.
- Si estás en la raíz, hay varios cursos y el mensaje no dice cuál, **pregunta**. Excepción: los pedidos sobre el workspace mismo (agregar un curso, tocar skills).
- Dentro de una sesión, mantén el curso establecido hasta que el usuario lo cambie.

## 4. Forma de trabajo: individual o en equipo

`perfil/perfil.md` define el **modo**.

| | Individual | Equipo |
|---|---|---|
| Diario | `courses/<slug>/JOURNAL.md` | `courses/<slug>/JOURNAL-<integrante>.md`, uno por persona |
| STATE | Uno por curso | Uno por curso, con una sección "Falta — <integrante>" por persona |
| git | Opcional | Obligatorio, con repositorio remoto compartido |
| Quién eres | El dueño del workspace | Se identifica con `git config user.name` y la tabla de integrantes del perfil |

**En modo equipo:**
- Al empezar: `git pull --rebase`. Si hay cambios locales sin subir, avisa antes de seguir.
- Cada integrante reescribe solo su sección del STATE y escribe solo en su JOURNAL.
- Nunca `git push --force` ni reescribir historia ya subida.
- Los conflictos se resuelven conservando los aportes de ambos; si no es obvio cómo, pregunta.
- Git no fusiona dos versiones de un `.docx`: si dos personas editan el mismo Word a la vez, hay que elegir una y rehacer a mano los cambios de la otra.

## 5. Estilo de trabajo

- Trabaja **punto por punto** en preguntas de examen y secciones de entregables, sin elaboración innecesaria.
- Prefiere **texto listo para pegar** (secciones de documento, tablas, mensajes al equipo) sobre explicaciones largas.
- Mantén la **criticidad**: señala inconsistencias entre los ejemplos del docente y sus reglas.
- Los mensajes de coordinación son cortos y directos: `shared/templates/whatsapp-message.md`.

## 6. Entregables en Word

- El Word que el usuario edita a mano es la **fuente de verdad**. Los `.md` de `deliverables/` son borradores para pegar.
- Antes de rehacer un bloque que ya se pegó, pide la versión actual o pregunta qué cambió. Si el Word cambió desde tu última versión, son ediciones del usuario o del equipo: aplica tus cambios **sobre esa versión** y nunca regeneres el documento encima.
- Si editas un `.docx` con código, guarda antes un respaldo y verifica con un diff de texto que solo cambió lo pedido.

## 7. Evidencia del uso de IA

Las universidades piden cada vez más que se declare el uso de IA. Cada curso lleva tres registros, que se llenan **al momento** y no al final:

| Registro | Qué guarda |
|---|---|
| `deliverables/registro-uso-ia.md` | Cada uso relevante de IA: fecha, herramienta, tarea, instrucción resumida y revisión humana |
| `deliverables/registro-errores-ia.md` | Cada salida de IA que resultó falsa o incumplía un criterio, y cómo se detectó |
| `deliverables/decisiones-humanas.json` | Cuando la IA recomienda y una persona decide (por ejemplo, el cribado de artículos), la decisión humana guardada aparte de la recomendación |

Las plantillas están en `shared/templates/`. Las transcripciones completas de las sesiones de los agentes (`~/.claude/projects/`, `~/.codex/sessions/`) son el respaldo literal de prompts y respuestas. Claude Code las borra a los 30 días si no se configura `"cleanupPeriodDays"` en `~/.claude/settings.json`: `iniciar-workspace` lo recuerda.

## 8. Privacidad

- No subas a un servicio de IA datos sensibles de terceros (empresas, personas, salud, finanzas) sin anonimizarlos antes.
- En planes personales de algunos proveedores, las conversaciones pueden usarse para entrenar modelos generales. Revisa la configuración de privacidad de tu cuenta.
- No subas al repositorio claves ni credenciales. Las API keys viven fuera del workspace (por ejemplo, `~/.config/elsevier/apikey`).
- Si el workspace se comparte, revisa antes que no lleve material de otros cursos ni datos personales.

## 9. Memoria persistente

| Archivo | Quién escribe | Cuándo | Rol |
|---|---|---|---|
| `STATE.md` | El agente | Al cerrar sesión | "Dónde vamos": se reescribe |
| `JOURNAL*.md` | El agente | Al cerrar sesión | "Qué hicimos": append-only |
| `decisions/ADR-XXX.md` | El agente propone, el usuario confirma | Cuando se toma una decisión de largo plazo | Registro auditable de decisiones |

- **Al iniciar sesión en un curso**: lee su `CLAUDE.md`, su `STATE.md`, el índice `decisions/README.md` y la última entrada del JOURNAL. Las ADR completas, solo si son relevantes al pedido.
- **Al cerrar sesión**: skill `cerrar-sesion`.
- **Nunca** sobrescribas una ADR ni borres entradas de un JOURNAL. Si una decisión se revierte, marca la anterior como "Superseded by ADR-XXX" y crea una nueva.

## 10. Formato

- Citas y referencias: la norma que fije `perfil/perfil.md`, por defecto **APA 7** (skill `apa7`). Las diferencias de la guía de la universidad van en un anexo del perfil y prevalecen sobre el estándar (sección 1).

## 11. Herramientas

- **Diagramas**: draw.io, con el XML `.drawio` generado con Python. Para UML, el skill `uml-architecture`. Exporta a PNG y revísalo una vez.
- **PDF** preferido para los materiales del docente.
- Los scripts de los skills necesitan Python 3. Las dependencias están en el `README.md`.

## 12. Skills

Claude Code los activa por su descripción. **Codex, Cline y otros agentes no los cargan solos**: antes de una tarea que cubra un skill, lee su `SKILL.md` y sigue el procedimiento. Los scripts (`scripts/*.py`) se corren igual con cualquier agente. Ejemplo: "cierra sesión" equivale a leer `.claude/skills/cerrar-sesion/SKILL.md` y aplicarlo.

| Skill | Para qué |
|---|---|
| `iniciar-workspace` | Primer uso: perfil de la universidad y forma de trabajo; demo opcional |
| `agregar-curso` | Crear un curso a partir de `courses/_template` |
| `cerrar-sesion` | Actualizar STATE, JOURNAL y ADR; en equipo, sincronizar con git |
| `apa7` | Citas y referencias en APA 7 |
| `verificar-referencias` | Comprobar que las referencias existen y cumplen los criterios del curso |
| `buscar-articulos` | Revisión de literatura reproducible: Scopus (API o CSV), WoS, PRISMA y cribado asistido |
| `informe-articulo` | Informe de un artículo desde su texto completo, con la página de cada dato |
| `revisar-entregable` | Revisión de un entregable contra su rúbrica, como un asesor senior |
| `uml-architecture` | Diagramas UML de componentes, paquetes y despliegue |

Los skills propios de un curso van en `courses/<slug>/.claude/skills/`. Los de una universidad, en `perfil/skills/`.

## 13. Cosas que NO hacer

- No modificar archivos en `courses/<slug>/docs/`: son materiales oficiales, de solo lectura.
- No borrar ni modificar entradas de un JOURNAL, ni escribir en el JOURNAL de otra persona.
- No aplicar las reglas de un curso a otro sin que el usuario lo pida.
- No presentar como regla del docente lo que es criterio propio.
- No usar herramientas para "humanizar" textos generados por IA ni para burlar detectores: contradice la declaración de uso ético de IA.
