# Fase 3A.1 — incremento 1 aprobado

Objetivo: que la aceptación pruebe el fuente actual, no bytecode previo.

Cambios: verification_worker.py materializa workspace y aceptación en árboles
temporales nuevos, excluyendo .git, __pycache__, .pyc y .pyo. Ejecuta con -I,
sin escribir bytecode; conserva checks del original y verifica también que la
copia fuente/aceptación no cambie. No elimina cachés originales. No es sandbox OS.

Regresión RED antes del cambio: 7 tests nuevos, 6 fallos, incluido el falso PASS
exacto (caché 7/fuente 9 con tamaño/timestamp coincidentes). Después: 7/7 PASS,
incluido fuente correcto, bytecode sin fuente, mutación de copia, gate/dependientes,
Fase 2 y aceptación histórica limpia (12 + 6 + 6 casos).

Suite completa: **76/76 PASS**, incluidos los 69 anteriores, en 111.712 segundos.
Evidencia: evidence/phase3a1/increment1-{red,targeted,all-tests}.log.

Revisión técnica del diff y evidencia: gates y hashes del orquestador no se
debilitan; ambos caminos supervised/pipeline comparten el runner corregido;
un FAIL conserva diagnóstico e impide aprobación, checkpoint y dependientes.
Las respuestas IA de estos tests son inyectadas, no inferencia real.

Los 341 hashes de preservación siguen iguales, incluida SQLite original,
sesiones/checkpoints históricos y especificación. No integración externa.
Incremento 2 todavía no iniciado al cerrar este checkpoint.
