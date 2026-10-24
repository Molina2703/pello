# Pello Fase 2 — resultado observado

## Actualización tras el intento autorizado

El usuario autorizó un nuevo intento. `phase2-leads-authorized` se detuvo antes
de la inferencia al intentar reabrir desde otro proceso un hilo todavía vacío:
`no rollout found for thread id`. Hubo una reserva de operación, **cero llamadas
a `thread.run`**, y ningún plan, implementación ni revisión reales. Se conserva
su informe en `evidence/phase2/authorized-blocked-cycle/`.

El ciclo de vida fue corregido: un único worker SDK vive durante el ciclo,
mantiene dos hilos separados y conserva el handle del supervisor para revisar.
Cada hilo nuevo se crea, se registra en SQLite y recibe su primer turno en el
mismo proceso. El worker se cierra al terminar o bloquearse el ciclo. No se
fuerza la toma de sesiones que otro proceso tenga activas.

La última suite pasó **42 pruebas: 34 unitarias y 8 de integración local**.
Incluye persistencia previa al primer turno y reutilización del handle durante
la revisión. Un ensayo SDK sin inferencia comprobó dos solicitudes sucesivas
por rol en el mismo worker, IDs estables y distintos, y cierre limpio:
`evidence/phase2/retained-worker-preflight/result.json`. Los hilos fueron
`01a16c40-9178-76d1-998d-d6bca142e09d` (supervisor) y
`01a16c40-9405-7591-9841-28ead4f88ed5` (ejecutor).

La preparación de hilos vacíos en procesos distintos **no basta** para probar
su reanudación; la evidencia inicial de preparación debe interpretarse con esta
limitación. No se inició automáticamente un tercer ciclo. El ciclo real de IA
sigue **IMPLEMENTED / UNVERIFIED** hasta un nuevo intento autorizado.

## Resultados iniciales conservados

**Estado: IMPLEMENTED / UNVERIFIED para el ciclo real completo.** La única
demostración intentada quedó **BLOCKED antes del primer turno de modelo**.
No se declara aprobada la Fase 2 ni terminado Pello V1.

## Implementación y pruebas

- Supervisor de IA con contexto acotado y salida estructurada mediante SDK.
- Mensajes Pydantic, correlación proyecto/tarea y plan secuencial persistente.
- Puente Python en SQLite, mediante tablas adicionales sin destruir las previas.
- Sesiones separadas por rol, creación/reanudación y registro del último turno.
- Flujo CLI: planificación -> ejecución -> verificación independiente -> revisión.
- Límite de tres operaciones; sin reintentos, reparación ni siguiente tarea.
- Rechazo de falsas aprobaciones, cero pruebas, hilos duplicados, cambios de
  pruebas/código y recuperación ambigua. Resultados del ejecutor son afirmaciones;
  cambios de archivos y pruebas son observaciones independientes de Python.

| Verificación | Resultado | Clasificación |
| --- | --- | --- |
| Línea base anterior | 4 pruebas originales aprobadas | REAL LOCAL VERIFIED |
| Pruebas unitarias finales | 31 aprobadas, incluidas las 4 originales | MOCK VERIFIED / REAL LOCAL VERIFIED |
| Integración local con modelos inyectados y SQLite/verificador reales | 7 aprobadas | MOCK VERIFIED / REAL LOCAL VERIFIED |
| Total automatizado | 38 aprobadas | No demuestra razonamiento real de IA |
| Regresión del demo clínico original | 2 intentos, 1 corrección, 8 pruebas finales aprobadas | MOCK VERIFIED |
| Catálogo y autenticación | SDK 0.163.0; gpt-6-luna disponible con esfuerzo low; ChatGPT | REAL LOCAL VERIFIED |
| Preparación SDK corregida | 2 hilos distintos creados, sin inferencia | REAL LOCAL VERIFIED |
| Ciclo real supervisor/ejecutor/revisión | No ejecutado; 0 turnos | BLOCKED |
| Aceptación del nuevo módulo leads.py | No ejecutada en demostración real | IMPLEMENTED / UNVERIFIED |

## Bloqueo real y corrección

La única orden real fue:

```powershell
.\pello.cmd supervised --spec examples\leads\SPEC.md --suite examples\leads\acceptance --project-id phase2-leads-first --model gpt-6-luna --effort low --timeout 180
```

Terminó con código **2**, durante la preparación del supervisor. No hubo plan,
decisión de supervisor, turno de ejecutor, módulo generado ni revisión de IA.
La causa fue `invalid transport in mcp_servers."node_repl"`: entrecomillar un
identificador normal en una opción `-c` creó otra entrada MCP inválida.

Se corrigió la construcción de opciones y se añadieron dos pruebas de regresión.
Los nombres con caracteres especiales se rechazan de forma segura. Luego se
comprobó exclusivamente la inicialización SDK, sin llamar `thread.run`:

- Supervisor: `01a16c33-4748-72c1-b37d-99643b131943`, permiso solicitado `read-only`.
- Ejecutor: `01a16c33-56a7-7323-b480-46a54b7c220c`, `workspace-write`.
- Modelo: `gpt-6-luna`, razonamiento bajo; cero turnos de inferencia.

Estos hilos de diagnóstico y sus resultados están guardados en archivos. El
almacenamiento SQLite de sesiones/último turno y la reanudación entre fases se
probaron con respuestas inyectadas; falta comprobarlos durante el ciclo real.
El proyecto bloqueado se conserva, sin borrar ni reescribir su historia.

No se hizo otro intento porque la solicitud dice:
**“Do not retry a blocked live demonstration automatically.”**
Por tanto, la Fase 2 necesita autorización para una nueva demostración acotada.

## Archivos y evidencia

Nuevos módulos: `messages.py`, `bridge.py`, `ai_supervisor.py`, `supervised.py` y
`verification_worker.py`. Modificados: `cli.py`, `codex_worker.py`, `engines.py`
y `supervisor.py`. También se corrigió `codex_executed`: intentar un turno ya no
se confunde con haberlo completado.

Nuevas pruebas: `tests/phase2_support.py`, `test_phase2_messages.py`,
`test_phase2_bridge.py`, `test_phase2_integration.py`, `test_phase2_worker.py`.
Fixture: `examples/leads/SPEC.md` y suite externa con 12 pruebas. Documentación:
`PHASE2.md`, `DECISIONS.md`, actualizaciones de README/SPEC/PLAN/STATE.

Checkpoint anterior: `3a9b0fe`, rama `codex/pello-phase2`. Copia previa de la base:
`evidence/phase2/jobs-before-phase2.sqlite3` (solo local). Evidencia de esta fase:

- `evidence/phase2/baseline-tests.log`
- `evidence/phase2/automated-tests-final.log`
- `evidence/phase2/legacy-demo-regression.log`
- `evidence/phase2/model-catalog.json`
- `evidence/phase2/live-cycle-cli.log`
- `evidence/phase2/preflight-fixed/result.json`
- `runtime/supervised/phase2-leads-first/report.json` y su carpeta `evidence/`
- `reports/phase2-result.json`, resumen reproducible del estado observado.

## Cobertura actual de los criterios V1

| Criterio | Evidencia actual |
| --- | --- |
| AC01 especificación -> plan persistente | MOCK VERIFIED; pendiente con supervisor real |
| AC02 supervisor real instruye al ejecutor | IMPLEMENTED / UNVERIFIED |
| AC03 transferencia automática Python | MOCK VERIFIED; pendiente extremo a extremo real |
| AC04 Codex modifica archivos | REAL SDK VERIFIED en el smoke histórico de Fase 1; no en Fase 2 |
| AC05 verificación independiente | REAL LOCAL VERIFIED; nueva fixture real pendiente |
| AC06 reparación autónoma real | NOT IMPLEMENTED; mock anterior no satisface este criterio |
| AC07 sesiones independientes persistentes | MOCK VERIFIED; creación SDK real sin turnos confirmada |
| AC08 rotación con contexto durable | NOT IMPLEMENTED, Fase 3 |
| AC09 recuperación segura | MOCK VERIFIED para reinicio ordinario; efectos ambiguos bloquean |
| AC10 varias tareas dependientes reales | NOT IMPLEMENTED; esta fase ejecuta solo una |
| AC11 informes basados en evidencia | REAL LOCAL VERIFIED, con bloqueo real reflejado |
| AC12 evaluación reproducible | MOCK VERIFIED / REAL LOCAL VERIFIED; evaluación V1 completa pendiente |

## Próximo paso y límites

Paso inmediato: autorizar **un nuevo intento de máximo tres turnos reales**, con
la configuración corregida. Debe planificar, implementar `leads.py`, ejecutar las
12 pruebas independientes, revisar los resultados y detenerse. No reintentar si
vuelve a bloquearse. No se debe presentar la preparación de sesiones como prueba
de razonamiento supervisor real.

Después de aprobar esa demostración, la siguiente tarea exacta de Fase 3 será
añadir rotación configurable por rol y reconstrucción del contexto desde las
tablas existentes, comprobando continuidad sin repetir tareas completadas.
No se inició Fase 3. Continúa pendiente un aislamiento de SO más fuerte para
Python generado no confiable; `-I`, hashes y timeout no constituyen esa frontera.
