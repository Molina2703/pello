# Pello — auditoría previa a Fase 3A

Base comprobada: 61f52e7, codex/pello-phase2. Rama nueva: codex/pello-phase3a.
Se conservaron el ZIP y el informe de contexto posteriores a esa base. Backup
SQLite en evidence/phase3a/jobs-before-phase3a.sqlite3 y filas originales en
baseline-tables.json. Archivo original de instalación preservado en Downloads.

Límites efectivos encontrados:

- Bridge.reserve: tres operaciones por proyecto.
- pello_exchanges: UNIQUE(project_id,kind), impide intercambios repetidos.
- pello_operations: fases plan/execute/review sin dimensión task/attempt.
- SupervisedCycle: secuencia fija hasta REVIEWED de una tarea, sin siguiente tarea.
- Dos roles persistidos y worker retenido, reutilizables.
- Contexto anterior sin historial de dependencias verificadas.

Cambio mínimo: nuevo pipeline sobre SupervisedCycle y nuevas tablas de intentos,
intercambios/operaciones/checkpoints con claves por incremento/intento/fase. Se
reutilizan SDK, permisos, SQLite, Git y runner. El límite de tres sigue intacto en
supervised. El worker admite esfuerzo high y modelo por turno sobre handles retenidos.
Sin dependencias adicionales, broker ni framework general. Requisito Python
corregido a 3.11: el worker ya dependía de tomllib. Entorno probado: 3.12.6.
