# Checklist — Cierre de sesión

Resumen del skill `cerrar-sesion`, para agentes que no cargan skills solos. Los campos **modo**, **git** y **cierre** salen de `perfil/perfil.md`.

1. **Quién y qué**: el curso trabajado; en modo equipo, el integrante (`git config user.name` → tabla del perfil).
2. **Modo equipo**: `git pull --rebase` antes de preparar nada.
3. **STATE.md**:
   - individual: se reescribe;
   - equipo: solo la sección "Falta — <integrante>" y las líneas comunes que cambiaron.
4. **JOURNAL**: entrada nueva al final, con Trabajado, Archivos tocados, Aprendizajes (opcional) y Notas. Va en `JOURNAL.md` en modo individual y en `JOURNAL-<integrante>.md` en equipo.
5. **Registros de IA**: errores detectados y decisiones humanas de la sesión, en `deliverables/`.
6. **ADR**: si hubo una decisión de largo plazo, crearla como Propuesta y agregarla al índice.
7. **Confirmar** el plan si `cierre: confirmar`.
8. **Escribir**: STATE → JOURNAL → registros → ADR.
9. **Git**: add solo de los archivos de la sesión, commit con el curso como prefijo y, con remoto, push. Nunca `--force`.
10. **Informar** en un mensaje corto.
