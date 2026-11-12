# Changelog

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/), y las versiones, [SemVer](https://semver.org/lang/es/). Mientras la versión sea 0.x, la estructura puede cambiar.

## [0.1.0] — 2026-11-11

Primera versión. Deriva del workspace multicurso del autor y de un proyecto de investigación en equipo, generalizados y sin datos de cursos reales.

### Agregado
- `AGENTS.md` y `CLAUDE.md` genéricos, con precedencia docente > institución > estándar y modo individual o en equipo.
- Skill `iniciar-workspace`: perfil de la universidad al primer uso y demo con la UPC como ejemplo.
- Skills `agregar-curso` y `cerrar-sesion`, este con modo individual o en equipo y cierre con o sin confirmación.
- Skill `apa7`, general, con el estándar APA y las diferencias locales en el perfil.
- Skills de investigación:
  - `verificar-referencias`, con política de cuartiles y antigüedad configurables;
  - `buscar-articulos`, con las preguntas de investigación configurables en `cadenas.json`;
  - `informe-articulo`;
  - `revisar-entregable`.
- Skill `uml-architecture`.
- Registros de evidencia de IA: uso, errores detectados y decisiones humanas.
- Perfil de ejemplo `perfiles-ejemplo/upc/` y curso ficticio `ejemplos/cursos/seminario-demo/`.
