# Pello Fase 2 — REAL SDK VERIFIED

La Fase 2 quedó verificada con un ciclo real de supervisor, ejecutor y revisión,
sin transferencia manual de mensajes. **Pello V1 completo sigue pendiente.**
Fecha de usuario: 2026-10-23, America/Bogota; evidencia técnica en UTC.

## Resultado

| Comprobación | Resultado |
| --- | --- |
| Proyecto / tarea | `phase2-leads-retained` / `T1` |
| Configuración | SDK 0.163.0, ChatGPT, `gpt-6-luna`, razonamiento `low` |
| Turnos SDK reales | 3: planificación, desarrollo, revisión |
| Decisión inicial | `CONTINUE`, una tarea con criterios y dependencias persistidos |
| Salida del ejecutor | `leads.py`, validación y normalización determinista de leads ficticios |
| Pruebas independientes | 12 aprobadas, 0 fallidas, 0 omitidas |
| Decisión final del supervisor | `COMPLETE`: recibió los resultados reales del verificador |
| Suite local final | 43 aprobadas: 34 unitarias y 9 de integración local |
| Demo clínico anterior | Conservado: 2 intentos, 1 corrección, 8 pruebas finales aprobadas |
| Reapertura del proyecto terminado | Código 0, ningún turno ni ejecución adicional |
| Integridad | Suite y código coinciden con hashes; SQLite correcto; datos previos conservados |

Las pruebas de integración local usan respuestas inyectadas y procesos/SQLite
reales. Se distinguen del ciclo de IA real anterior; no se presentan mocks como
prueba de razonamiento supervisor.

## Componentes y archivos

- `ai_supervisor.py`: contexto acotado, instrucciones por rol, conexión SDK.
- `messages.py`: tareas, decisiones, resultados y verificaciones validados.
- `bridge.py`: migración aditiva, proyectos/tareas/sesiones/exchanges/operaciones.
- `supervised.py`: un ciclo finito, correlación, reservas y gates de verificación.
- `verification_worker.py`: unittest independiente, JSON y conteo correcto de subtests.
- Modificados `cli.py`, `codex_worker.py`, `engines.py` y `supervisor.py`: orden
  `supervised`, worker SDK retenido, persistencia antes del primer turno, salida
  estructurada, permisos, timeout y cierre, informe de ejecución basado en turnos
  completados. No se reinstaló el proyecto ni se agregaron servicios externos.
- Fixture `examples/leads/`: especificación Markdown y 12 pruebas externas.
- Pruebas `test_phase2_messages.py`, `test_phase2_bridge.py`,
  `test_phase2_integration.py`, `test_phase2_worker.py` y soporte inyectado.
- Actualizados README/SPEC/PLAN/STATE/DECISIONS y guía `PHASE2.md`.

## Sesiones y evidencia

| Rol/fase | Thread ID | Turn ID |
| --- | --- | --- |
| Supervisor / plan | `01a16c44-6047-7783-8696-388dd4198e63` | `01a16c44-620a-7101-9071-a44196165b48` |
| Ejecutor | `01a16c44-820c-71c3-bd9c-54c7dfa3fa15` | `01a16c44-83ac-7953-ad6c-4e62489a1510` |
| Supervisor / revisión | mismo hilo del supervisor | `01a16c44-f0f2-70c3-b386-0a6ff9c2a568` |

Los dos roles y sus últimos turnos exitosos están en SQLite. El supervisor
solicitó acceso de solo lectura; el ejecutor, escritura en el workspace sin
raíces adicionales. Los tests permanecieron fuera de esa área y conservaron su
hash. Se desactivaron MCP heredados, apps/plugins, web search y agentes extra.

Evidencia principal: `evidence/phase2/verified-live-cycle/`, con prompts,
esquemas, respuestas SDK, IDs, pruebas, snapshots, código y manifiesto SHA-256.
Original operativo: `runtime/supervised/phase2-leads-retained/`.
Resumen legible por máquina: `reports/phase2-result.json`.
Suite completa: `evidence/phase2/final-all-tests.log`.
Reapertura: `evidence/phase2/completed-project-reopen.log`.

Los contadores SDK finales por hilo suman 77.060 tokens de entrada y 1.555 de
salida, 78.615 totales; 49.152 de entrada estaban en caché. Son contadores, no un
cargo USD verificado. La revisión incluye acumulativamente la planificación;
no se suma esta última por segunda vez.

## Incidencias corregidas y preservadas

Dos intentos previos se bloquearon antes de inferencia: uno por sintaxis de
opciones MCP y otro por reabrir un hilo vacío en un proceso nuevo. Ambos informes
se conservan; cada nuevo intento tuvo autorización humana explícita. No hubo
reintentos automáticos ni turnos de reparación. **La fase consumió tres turnos
SDK reales en total.**

El worker ahora crea cada hilo, persiste su ID antes del primer turno y conserva
ambos handles durante el ciclo. Esto evita depender de la persistencia de un
hilo vacío y permite que la revisión use el mismo hilo supervisor. El worker se
cierra al terminar. La toma de una sesión con otro escritor activo no se fuerza;
se bloquea para reconciliación. Los informes anteriores están preservados en
`PHASE2-PRE-LIVE.md` y en las carpetas de evidencia de cada intento.

## Criterios V1

| Criterio | Evidencia alcanzada |
| --- | --- |
| AC01 especificación -> plan persistente | REAL SDK VERIFIED |
| AC02 supervisor real instruye al ejecutor | REAL SDK VERIFIED |
| AC03 transferencia Python sin copia manual | REAL SDK VERIFIED |
| AC04 modificaciones de código reales | REAL SDK VERIFIED |
| AC05 verificación independiente | REAL SDK VERIFIED / REAL LOCAL VERIFIED |
| AC06 corrección autónoma tras fallo | NOT IMPLEMENTED en IA real; solo simulación local |
| AC07 sesiones independientes persistentes | REAL SDK VERIFIED para IDs, roles y turnos exitosos |
| AC08 rotación sin perder contexto | NOT IMPLEMENTED, Fase 3 |
| AC09 recuperación de interrupciones | MOCK VERIFIED; reapertura terminada REAL LOCAL VERIFIED; interrupción SDK real pendiente |
| AC10 varias tareas dependientes reales | NOT IMPLEMENTED; este ciclo ejecutó una tarea |
| AC11 informes según evidencia | REAL LOCAL VERIFIED / REAL SDK VERIFIED |
| AC12 evaluación reproducible | REAL LOCAL VERIFIED para esta suite; evaluación V1 completa pendiente |

## Próximo paso exacto

Fase 3, solo mediante una nueva solicitud: implementar una política configurable
de rotación por rol y reconstruir contexto acotado desde especificación, plan,
decisiones, tareas y pruebas guardadas. Verificar que un hilo reemplazado pueda
continuar sin repetir tareas completadas. No se inició esa fase.

Siguen pendientes la recuperación avanzada de operaciones SDK interrumpidas,
reparación autónoma, tareas múltiples y aislamiento fuerte del verificador.
Python `-I`, hashes y timeout no aíslan por completo código malicioso del SO.
