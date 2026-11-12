# cordada-ai

**A harness for students.** *[English below](#english)*

En montañismo, una **cordada** es el equipo atado a la misma cuerda: cada uno asegura a los demás. Aquí van atados tú, tus agentes de IA y las reglas de tus cursos.

**No es un autocorrector.** Es un workspace que les da a los agentes de IA (Claude Code, Codex, Cursor, Copilot…) **memoria por curso**, **reglas con fuente** y **evidencia del uso de IA**, para que trabajar con IA en la universidad sea útil, verificable y honesto.

## Qué resuelve

| Problema | Cómo lo resuelve |
|---|---|
| Cada conversación con la IA empieza de cero | Cada curso tiene su `STATE.md` (dónde vas), su `JOURNAL.md` (qué hiciste) y sus decisiones (`decisions/`) |
| La IA aplica reglas genéricas o las inventa | Las reglas viven en el `CLAUDE.md` del curso, **cada una con su fuente** (sílabo, rúbrica, minuto de la clase). Precedencia: docente > universidad > estándar |
| La IA inventa citas | Toda referencia se verifica contra Crossref, OpenAlex y SCImago antes de usarla |
| Te piden declarar el uso de IA | Tres registros por curso: uso, errores detectados y decisiones humanas frente a las recomendaciones de la IA |
| Trabajas en equipo | Modo equipo con git: memoria compartida y un diario por integrante |

## Principios

1. **Sourcing discipline**: siempre se distingue lo literal del material del curso de lo que es inferencia.
2. **El docente manda**: si su regla diverge del estándar (APA, ISO, UML), gana la del docente, y se anota la divergencia.
3. **La IA propone, la persona decide**, y las dos decisiones se guardan por separado.
4. **Memoria explícita y auditable**: archivos de texto que puedes leer, versionar y mostrar, en lugar de memoria opaca.
5. **Agnóstico al agente**: `AGENTS.md` es el estándar abierto que leen Claude Code, Codex, Cursor y otros.

## Empezar

```bash
# 1. En GitHub: "Use this template" (tu copia puede ser privada). No hagas fork: un fork de un repositorio público no puede ser privado.
git clone https://github.com/<tu-usuario>/<tu-workspace>.git
cd <tu-workspace>

# 2. Abre tu agente en la raíz
claude          # Claude Code (recomendado), o tu agente preferido
```

En la primera sesión, el skill **`iniciar-workspace`** te pregunta **tu universidad**, tus normas académicas y si trabajas solo o en equipo. Si solo quieres verlo funcionar, responde **"demo"**: se instala un curso ficticio, con la UPC como universidad de ejemplo.

Después:
- *"Agrega el curso de Gerencia de Proyectos"* crea el curso.
- *"Para el curso de gerencia, ¿qué falta para el próximo entregable?"* carga sus reglas y su estado.
- *"Cierra sesión"* guarda el estado y el diario.

## Skills incluidos

| Skill | Para qué |
|---|---|
| `iniciar-workspace` | Primer uso: universidad, normas y forma de trabajo; demo opcional |
| `agregar-curso` | Crear un curso con sus reglas, su memoria y sus registros de IA |
| `cerrar-sesion` | Persistir STATE, JOURNAL y decisiones; en equipo, sincronizar con git |
| `apa7` | Citas y referencias APA 7, con las diferencias de tu universidad |
| `verificar-referencias` | ¿Existe? ¿Cumple los criterios del curso? DOI, año, tipo, cuartil SJR y retracciones |
| `buscar-articulos` | Revisión de literatura reproducible: Scopus (API o CSV), WoS, PRISMA y cribado asistido |
| `informe-articulo` | Informe de un artículo desde su texto completo, con la página de cada dato y una guía de defensa |
| `revisar-entregable` | Revisión como asesor senior contra la rúbrica; sirve para que otra sesión u otro modelo revise |
| `uml-architecture` | Diagramas UML de componentes, paquetes y despliegue |

## Estructura

```
AGENTS.md            reglas para cualquier agente
CLAUDE.md            índice de cursos y lo específico de Claude Code
perfil/              tu universidad y forma de trabajo (lo crea iniciar-workspace)
perfiles-ejemplo/    perfil de muestra (UPC) y un skill institucional de ejemplo
courses/_template/   plantilla de curso
courses/<curso>/     CLAUDE.md, STATE.md, JOURNAL.md, decisions/, docs/, deliverables/
ejemplos/            curso de demostración
shared/templates/    ADR, registros de IA, perfil, cierre de sesión
.claude/skills/      los skills
```

## Requisitos

- Un agente que lea `AGENTS.md`. Con Claude Code, los skills se activan solos.
- Python 3 para los scripts, con `pip install python-docx lxml`. También `pdftotext` (poppler): `brew install poppler` o `apt install poppler-utils`.
- Opcional: una API key de Elsevier para Scopus (https://dev.elsevier.com) y el CSV anual de SCImago (https://www.scimagojr.com/journalrank.php → *Download data*), guardado en `perfil/referencia/`.

## Privacidad e integridad académica

- No subas a la IA datos sensibles de terceros sin anonimizarlos, y revisa si tu proveedor usa tus conversaciones para entrenar.
- Claude Code borra las transcripciones a los 30 días. Si son tu evidencia de uso de IA, configura `"cleanupPeriodDays"` en `~/.claude/settings.json`.
- cordada-ai no reemplaza tu lectura ni tu criterio: el docente evalúa lo que tú puedes defender.

## Licencia y cita

- Código y skills: [MIT](LICENSE). Documentación del método: [CC BY 4.0](LICENSE-DOCS.md).
- Si lo usas en un trabajo académico, cítalo con [`CITATION.cff`](CITATION.cff) (GitHub muestra "Cite this repository").
- Creado por **Joel Elias Sulca Cordova**. Gran parte del texto se redactó con Claude Code siguiendo el diseño del autor: el método se usó para construirse a sí mismo.

---

<a id="english"></a>

## English

In mountaineering, a ***cordada*** is a rope team: climbers tied together, each one securing the others. Here, you, your AI agents and your course rules move together.

**Not an autograder.** cordada-ai is a workspace that gives AI coding agents (Claude Code, Codex, Cursor, Copilot…) **per-course memory**, **rules with their source**, and **evidence of AI use**, so working with AI at university stays useful, verifiable and honest.

- **Per-course memory**: each course has a `STATE.md` (where you are), a `JOURNAL.md` (what you did) and `decisions/` (ADRs).
- **Rules with sources**: each instructor rule is stored with its source (syllabus, rubric, lecture minute). Precedence: instructor > university > standard (APA, ISO…).
- **No invented citations**: references are checked against Crossref, OpenAlex and SCImago before use.
- **Evidence of AI use**: per-course logs of AI use, AI errors caught, and human decisions kept separate from AI recommendations.
- **Solo or team mode**: team mode uses git, with shared memory and one journal per member.
- **Agent-agnostic**: built on `AGENTS.md`. Optimized for Claude Code.

**Quick start**: click "Use this template" (not fork, so your copy can be private), open your agent at the root, and the `iniciar-workspace` skill asks for **your university**. Answer **"demo"** to try a fictional course that uses UPC (Peru) as a sample university profile. The skills and docs are currently in Spanish; agents work fine in English.

License: code under MIT, documentation under CC BY 4.0. Created by Joel Elias Sulca Cordova. Not affiliated with any university.
