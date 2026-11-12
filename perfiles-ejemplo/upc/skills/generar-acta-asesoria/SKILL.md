---
name: generar-acta-asesoria
description: Genera la siguiente Acta de Reunión (Word .docx) de una asesoría semanal de proyecto, a partir del acta anterior y de los apuntes de sesión que el docente envía por correo (secciones "Agenda" y "Compromisos"). Conserva el formato oficial editando solo el texto que cambia y deja las firmas en blanco. Ejemplo de skill propio de una universidad (perfil UPC). Actívalo cuando el usuario pegue el correo de apuntes del docente o pida "genera el acta N".
---

# Generar el acta de una asesoría

*Skill de ejemplo del perfil UPC. Para usarlo en tu workspace, cópialo a `perfil/skills/` (si aplica a todos tus cursos) o a `courses/<slug>/.claude/skills/` (si es de un curso), y ajusta las rutas.*

## Por qué funciona así

El acta es un `.docx` oficial, con tablas, estilos y una tabla de firmas difícil de reconstruir. Lo que funciona es **partir del acta anterior** y editar con `python-docx` solo lo que cambia (número, fecha, agenda, compromisos), quitando las firmas. Así se conserva el formato exacto.

Dos errores reales que este skill evita:
1. **Reconstruir la agenda y los compromisos desde la transcripción de la reunión.** La fuente es el correo de apuntes del docente; la transcripción solo sirve de respaldo si el correo es ambiguo.
2. **Invertir el responsable de cada compromiso.** En el correo, el responsable va entre paréntesis al final del ítem ("Presentación de avances (Proyecto)"). El script lo extrae solo.

## Procedimiento

### 1. El correo de apuntes

Si el usuario lo pegó, guárdalo tal cual en un `.txt` temporal. Si no, **pídelo antes de seguir**. Reconstruir desde la transcripción solo se hace si el usuario confirma que no tiene el correo, y se deja dicho que es una reconstrucción.

Formato esperado:

```
Agenda
-Revisión de objetivos específicos
-Revisión del formato del trabajo

Compromisos
-Presentación de avances (Proyecto)
-Revisión de artefactos de gestión (Asesor)
```

### 2. El acta anterior

Busca la de número más alto en la carpeta de actas del curso (por ejemplo, `courses/<slug>/deliverables/actas/`).

### 3. Ejecutar

```bash
python3 <ruta-del-skill>/scripts/generar_acta.py \
  --previous "courses/<slug>/deliverables/actas/<CURSO>-<CODIGO>-Acta-<NN-1>.docx" \
  --output   "courses/<slug>/deliverables/actas/<CURSO>-<CODIGO>-Acta-<NN>.docx" \
  --numero <NN> --fecha <DD/MM/AAAA> \
  --apuntes <correo.txt> --fecha-maxima-compromisos <DD/MM/AAAA>
```

Opciones:
- `--hora-inicio` y `--hora-fin`, si cambiaron;
- `--codigo-proyecto` y `--nombre-proyecto`, si cambiaron respecto del acta anterior.

Lee la salida: avisa si un compromiso no traía responsable o si quedó una firma sin quitar.

### 4. Verificar

- La agenda y los compromisos coinciden con el correo, ítem por ítem, y ningún responsable quedó invertido.
- No quedan firmas del acta anterior.
- Recuerda al usuario que falta firmar y enviar el acta según la regla del curso: a quién se envía y en qué plazo (consúltalo en el `CLAUDE.md` del curso).

## Límites

- **Firmas**: quedan en blanco para firmar a mano.
- **Asistencia**: si alguien faltó, la celda se edita a mano.
- **Plantillas muy distintas**: el script ubica las tablas por el texto de su encabezado (`find_table`). Un cambio grande de plantilla puede requerir ajustar el script.
