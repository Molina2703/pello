# Pello — checkpoint previo a demostración Fase 3A

2026-10-24, America/Bogota. Base 61f52e7, rama codex/pello-phase3a.

- IMPLEMENTED: pipeline, contratos, intentos/exchanges, routing, checkpoints y CLI.
- TESTED WITH MOCKS / VERIFIED LOCALLY: 69 tests aprobados, incluidos los 43 previos.
- Suite final: evidence/phase3a/final-all-tests.log, 100.568 segundos.
- Pruebas iniciales preservadas: un defecto de detalle del bloqueo corregido;
  una expectativa de enum del test SDK ajustada a deny_all del SDK instalado.
- Verificador con intención durable: resultado completo se recupera sin repetir;
  interrupción sin resultado exige reconciliación. Ambos casos probados localmente.
- CLI/help, sintaxis Python/PowerShell y pip check correctos. Estado del proyecto
  real Phase 2 conservado. Python mínimo declarado ahora 3.11 por tomllib existente.
- Catálogo/autenticación consultados sin inferencia; Luna/Sol y esfuerzos disponibles.
- Inferencia real Fase 3A hasta este checkpoint: 0 turnos.
- Demo previsto: examples/quotes, T1 pricing y T2 quotes que consume T1;
  máximo cinco llamadas Luna/low, un intento por incremento, sin reintento del demo.
- Integración externa, rotación, scheduler y correo: NOT IMPLEMENTED.

Este checkpoint no es evidencia de que el nuevo camino ya funcionó con SDK real.
