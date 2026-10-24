# Pello — resultado Fase 3A

**24 de octubre de 2026, America/Bogota. Fase 3A completada dentro del alcance.**
Pipeline incremental **VERIFIED THROUGH REAL CODEX SDK** para dos incrementos
dependientes. **Pello V1 completo todavía no está operativo.**

## Resultado medido

| Comprobación | Resultado |
| --- | --- |
| Proyecto | phase3a-quotes-first, COMPLETE |
| Plan global | IA real, dos incrementos del contrato del dueño |
| T1 | pricing.py: normalización/validación de ítems y cálculo en centavos |
| T2 | quotes.py: consume pricing.normalize_item y genera cotización |
| Tests T1 | 6/6 aprobadas antes de permitir T2 |
| Tests tras T2 | 6/6 de T2 y 6/6 de regresión de T1 |
| Tests del demo | 12 únicos, 18 ejecuciones con regresión, sin fallos ni omisiones |
| Revisiones IA | PASS para ambos, con código/diff y resultados reales |
| Checkpoints | Dos commits consistentes; pricing.py conserva su hash durante T2 |
| Uso real | Cinco turnos gpt-6-luna / low: tres supervisor y dos ejecutor |
| Intentos | Uno por incremento, sin reparación ni reintento del demo |
| Tests del orquestador | 69 aprobados: 43 anteriores y 26 nuevos |
| Reapertura terminada | Código 0, siguen cinco operaciones y dos checkpoints; cero turnos adicionales |
| Conservación | Todas las filas previas preservadas, SQLite ok, ZIP original intacto |

T2 incluye una prueba observable de la llamada a pricing; el segundo módulo
consume realmente el primero. Los criterios reportados (12/12) son los contratos
cubiertos por suites aprobadas, no una auditoría individual del producto V1.

## Implementación

Plan global durable → incremento con dependencias aprobadas → implementar →
verificar → revisar según política → checkpoint → siguiente. Un fallo conserva
su intento y diagnóstico reproducible; la reparación es acotada y puede seleccionar
Sol según riesgo/historial. No reinicia el proyecto ni cambia la aceptación.
Cuota/límites, falta de progreso, efectos inciertos o diagnóstico de infraestructura/
especificación bloquean para reconciliación. Replan del contrato no es automático.

Tablas nuevas pello_pipeline_projects/attempts/exchanges/operations/checkpoints;
se reutilizan pello_projects/tasks/sessions y el adaptador SDK. supervised conserva
el límite histórico de tres turnos. Las operaciones e intercambios nuevos se
correlacionan por task/attempt/phase. Un lock de OS protege un escritor por proyecto.

Tester es Python determinista. Reviewer usa el supervisor SDK read-only; recibe
fuente, diff y tests y su PASS no sustituye un gate objetivo fallido. Frecuencia
every_increment o final, con revisión siempre para riesgo alto. No hay cuatro
procesos IA permanentes ni una llamada adicional de diagnóstico por cada unittest.

Resultados SDK o de verificación completos guardados se procesan sin repetirlos;
si faltan tras una operación incierta se bloquea. Checkpoints usan intención
PREPARED antes de Git y se reconcilian por padre/mensaje/fuente tras una caída.

Módulos nuevos: pipeline.py, pipeline_store.py, pipeline_contracts.py, model_policy.py.
Extendidos CLI y worker (modelo por turno, esfuerzo high). Nombres visibles Pello,
launcher UTF-8 y Python mínimo 3.11 por tomllib ya existente. Sin nuevas dependencias.

## Evidencia, sesiones y uso

- Implementación antes de inferencia: **30ed940**, base **61f52e7**,
  rama **codex/pello-phase3a**. Auditoría: PHASE3A-AUDIT.md.
- Supervisor: `01a16c8b-1568-7073-a78e-4ca5956536b9`.
- Ejecutor: `01a16c8b-306b-7b63-aec8-9e679cc73685`.
- Checkpoint T1: `1712620d24f3a059ec7913c7084ade204b326dc2`.
- Checkpoint T2: `6a9c4b2096d0414b062b214165bb0ac22298b886`.
- evidence/phase3a/verified-live-pipeline/: prompts, esquemas, respuestas, tests,
  fuente, reporte, IDs y manifiesto SHA-256. Resumen: phase3a-result.json.
- Logs en evidence/phase3a/: final-all-tests.log, live-demo.log y completed-reopen.log.
  Backup jobs-before-phase3a.sqlite3 local, ignorado por Git.

Contadores acumulados finales: **134.849 entrada, 1.515 salida, 136.364 total;
85.632 de entrada en caché**. Se cuenta una vez el último total de cada hilo.
No son facturación USD ni consumo total de la conversación de desarrollo.
No se usó Astra, API de pago ni Claude. Routing/repair Sol se probaron con
inyección, no inferencia Sol real. No se comparó este demo con un control monolítico:
la hipótesis de ahorro por incrementos todavía requiere un benchmark comparable.

## Clasificación y límites

| Categoría | Estado |
| --- | --- |
| IMPLEMENTED | Pipeline, persistencia y configuración declarativa de herramientas |
| TESTED WITH MOCKS | Repair/escalada, fallos, restauración, no duplicación y lock |
| VERIFIED LOCALLY | 69 tests, suites externas, Git/SQLite, integridad y conservación |
| VERIFIED THROUGH REAL CODEX SDK | Plan y dos incrementos con revisiones; cinco turnos |
| VERIFIED IN REAL EXTERNAL INTEGRATION | No alcanzado; ninguna operación n8n/Railway/Google |
| BLOCKED | Ninguno pendiente en esta demostración |
| NOT IMPLEMENTED | Integración externa ejecutable, rotación, recovery remoto completo, scheduler/correo y V1 completa |

El dueño todavía escribe manifiesto y suites; la IA planifica dentro de esa
descomposición, no se demuestra descomposición autónoma de una ficha extensa.
Herramientas por proyecto: referencias no secretas, límites/entorno/recursos y
verificación. Externas habilitadas se rechazan en esta fase. No se modificaron
workflows, sistemas de clientes ni configuración de credenciales.

Python -I, hashes y timeout no son sandbox fuerte de OS. Continuar un turno remoto
interrumpido o un hilo ocupado requiere reconciliación; no se garantiza exactly-once,
operación ininterrumpida ni reparto óptimo Luna/Sol.

## Próximo hito

Adaptador n8n DEV autorizado con allowlist, referencias seguras y diario/reconciliación
de operaciones externas. Después, piloto vertical con recurso realmente existente
y evidencia de ejecución. PLAN.md ordena las dependencias hacia aislamiento,
reparación real, rotación, continuidad Windows, correo y aceptación V1.
**Se detuvo el trabajo al terminar Fase 3A; ese hito no se inició.**
