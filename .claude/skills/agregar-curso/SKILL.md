---
name: agregar-curso
description: Crea un curso nuevo en el workspace a partir de courses/_template. Pide los datos mínimos (nombre, código, docente, ciclo, slug y keywords), prepara STATE, JOURNAL y los registros de uso de IA según el modo del perfil (individual o equipo) y agrega la fila al índice de CLAUDE.md. Actívalo cuando el usuario diga "agrega el curso de X", "crea un curso", "empiezo un curso nuevo", "añade la materia X" o algo equivalente.
---

# Agregar un curso

## Antes de empezar

Lee `perfil/perfil.md`. Si no existe, ejecuta primero `iniciar-workspace`. El modo (individual o equipo) define qué JOURNAL se crea.

## Procedimiento

### 1. Datos mínimos

Pide todo en **una sola pregunta**:
1. Nombre completo del curso.
2. Código del curso, si lo tiene.
3. Docente principal.
4. Ciclo o periodo (por ejemplo, 2027-1).
5. **Slug**: propón uno corto, en minúsculas y sin tildes (`gerencia-proyectos`). Confírmalo.
6. **Keywords**: propón entre 5 y 10 palabras con las que el usuario se referiría al curso ("para el curso de…"). Confírmalas.
7. ¿Tiene material (sílabo, rúbricas, enunciados, diapositivas)? Si sí, que lo tenga a mano para copiarlo a `docs/`.

### 2. Copiar la plantilla

```bash
cp -r courses/_template courses/<slug>
```

Si `courses/<slug>` ya existe, avisa y pide otro slug. No sobrescribas.

### 3. Llenar el `CLAUDE.md` del curso

Reemplaza los marcadores `<…>` de `courses/<slug>/CLAUDE.md` con los datos del paso 1. Las secciones de reglas del docente, entregables y criterios **quedan vacías**, con su indicación de "pendiente": se llenan con el material del curso, siempre con su fuente. No inventes reglas.

### 4. STATE, JOURNAL y registros

- `STATE.md`: "Sin trabajo iniciado. Curso creado el <fecha>."
  - En **modo equipo**, agrega una sección "Falta — <integrante>" por cada persona de la tabla del perfil.
- **JOURNAL**:
  - **Individual**: deja `JOURNAL.md`, con la primera entrada "Curso creado".
  - **Equipo**: renombra `JOURNAL.md` como `JOURNAL-<integrante>.md` y crea uno por cada integrante. Solo el de quien crea el curso lleva la primera entrada.
- **Registros de IA** (`AGENTS.md`, sección 7): copia a `courses/<slug>/deliverables/` las plantillas `registro-uso-ia.md`, `registro-errores-ia.md` y `decisiones-humanas.json` de `shared/templates/`.

### 5. Índice

Agrega la fila en la tabla "Índice de cursos" de `CLAUDE.md` raíz:

```
| `<slug>` | <nombre completo y código> | <ciclo> | <docente> | Activo | <keywords separadas por coma> |
```

Si otro curso terminó, cambia su estado a "Cerrado (<ciclo>)", pero no borres su fila.

### 6. Material del curso

Si el usuario tiene material, pídele que lo copie a `courses/<slug>/docs/`. Después ofrece leerlo para llenar el `CLAUDE.md` del curso: entregables y fechas, rúbricas, criterios de fuentes y reglas del docente, **cada una con su fuente** (archivo y página o minuto).

### 7. Reporte

Di qué se creó (rutas) y cómo empezar: "para el curso de <X>, …".

## Reglas

- No borres ni sobrescribas otros cursos.
- No inventes convenciones del docente: los marcadores quedan hasta que haya fuente.
- En modo individual, muestra el plan y confirma antes de escribir. En modo equipo, además haz commit y avisa que el otro integrante debe hacer pull.
- Los skills propios del curso se crean después, cuando el usuario los pida, en `courses/<slug>/.claude/skills/`.
