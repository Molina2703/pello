# Pello — resultado Fase 3A.1

**24 de octubre de 2026, America/Bogota. COMPLETE dentro del alcance correctivo.**
Base Python + SDK + SQLite + Git conservada. Preparado para iniciar un piloto
3B acotado mediante nueva instrucción; no se habilitó integración externa.

## A. Resultado ejecutivo

Aceptación del fuente actual corregida, Reviewer independiente en el pipeline,
perfiles por responsabilidad y roadmap alineados con V1.3. Sin bloqueadores
pendientes de 3A.1. No implica que Pello V1 completo esté terminado ni que las
operaciones externas estén ya habilitadas: 3B comienza con preflight y controles.

## B. Resultados por incremento

| Incremento | Cambios | Evidencia | Checkpoint |
| --- | --- | --- | --- |
| 1 | verification_worker.py, test_verification_source.py y contrato/reporte | RED: 6/7 tests nuevos fallaban. Después: 7/7 y 76/76 totales; aceptación histórica 12+6+6 | 59662816e6ad009632af79863f831a22e03caf21 |
| 2 | bridge.py, codex_worker.py, ai_supervisor.py, pipeline.py, pipeline_contracts.py, model_policy.py; tests de roles/worker/pipeline; política ejemplo y documentación | 10 tests de roles; 2 de transmisión/permisos; 87/87 finales, 123.660 s. Demo real de cinco turnos | Commit que incorpora este informe; SHA completo en la entrega final |

Incremento 1 fue probado, revisado y commiteado antes de comenzar 2. Los 69 tests
originales continúan; se actualizó la expectativa de dos a tres sesiones del
pipeline y el test del worker ahora comprueba el rol reviewer real. Las pruebas
anteriores del supervisor legacy siguen comprobando su configuración histórica.

Logs: evidence/phase3a1/increment1-red.log, increment1-targeted.log,
increment1-all-tests.log, increment2-targeted-final.log, increment2-worker-final.log
y final-all-tests.log. Respuestas de esos tests: **inyectadas**, no SDK real.

## C. Corrección del falso PASS

Antes, dont_write_bytecode impedía escribir caché pero Python podía leer .pyc
existente. Un cambio con igual tamaño/timestamp ejecutaba comportamiento antiguo.
Ahora el worker crea copias nuevas de workspace y aceptación sin .git,
__pycache__, .pyc ni .pyo; ejecuta desde ellas con -I y escritura de bytecode
deshabilitada. Comprueba además que las copias no cambien. Los hashes originales
y gates existentes permanecen. No borra ni altera las cachés del proyecto original.

Regresiones: caché 7/fuente 9 da FAIL; fuente 7 con caché 9 da PASS; bytecode sin
fuente no satisface aceptación; mutación de la copia invalida el resultado. FAIL
impide aprobación, checkpoint y dependientes y preserva diagnóstico reproducible.
Esto es consistencia de fuente, no sandbox OS frente a código malicioso.

## D. Reviewer independiente

Demostración real phase3a1-quotes-first:

| Responsabilidad | Thread ID |
| --- | --- |
| Planner | 01a16f22-7a4f-7e50-85c0-a8e0946b1118 |
| Executor | 01a16f22-d029-7c12-b9ed-942ff66244ab |
| Reviewer | 01a16f23-4ba7-7a63-8ecc-7df8f90e0e15 |

Reviewer recibe ficha, contrato, restricciones, dependencias verificadas, fuente,
diff, archivos observados y resultados deterministas. No se reenvían global_plan,
reasoning_summary, instrucciones privadas del Planner, narrativa del Coder ni
feedback privado previo. Los hilos tienen identidades únicas persistidas.

La configuración enviada al SDK es read-only/deny_all para Planner y Reviewer;
los model-turn-submitted.json lo registran. El worker transmite modelo/esfuerzo
por turno y el pipeline compara snapshots antes/después de revisar. Las dos
revisiones reales fueron PASS sin modificar fuente ni tests. Los tests rechazan
identidad compartida, mutación por Reviewer y cualquier intento de aprobar FAIL.
Se usa un worker SDK retenido; no cuatro procesos de agentes permanentes.

## E. Modelos

| Rol | Habitual | Demostrado ahora |
| --- | --- | --- |
| Planner | Sol High | gpt-6.1-sol/high, un turno real |
| Coder | Luna Medium | gpt-6-luna/medium, dos turnos reales |
| Reviewer | Sol High | gpt-6.1-sol/high, dos turnos reales |
| Tester | Determinista o variable | Python real; perfil IA opcional configurable, sin invocación IA de Tester |

role_profiles configura modelo/esfuerzo. Coder puede usar advanced por riesgo o
reintento; tests verifican escalada y perfiles más ligeros. Políticas completas
routine/advanced ya guardadas conservan sus elecciones y valores históricos.
Disponibilidad validada en catálogo; perfiles ausentes/no disponibles bloquean
sin sustitución. No Astra, API facturada ni cuota artificial 70–80%.

SDK instalado: 0.163.0. Catálogo y autenticación ChatGPT confirmaron disponibilidad
de los perfiles del demo. No fue necesario actualizar dependencias. Reparación y
escalada de un Coder fallido siguen **mock-only**; este demo pasó al primer intento.
Uso registrado SDK: 184118 entrada, 2429 salida, 186547 total, 135808 entrada en
caché. Se cuenta el último total una vez por hilo; no es factura USD.

## F. Preservación

Los 341 hashes originales siguen idénticos, incluida runtime/jobs.sqlite3,
sesiones/checkpoints anteriores y documentos canónicos. Migración v4 transaccional,
idempotencia y rollback probados; copia de la base real conserva todas las filas
de las 13 tablas. Los proyectos históricos Fase 2 y 3A reabren en la copia sin
inferencia, manteniendo cinco operaciones en 3A y sus checkpoints. La base
original no fue migrada durante este trabajo; se migrará al abrirla con el código
actual. Las referencias antiguas siguen accesibles.

El ciclo supervised histórico mantiene sus dos roles y evidencia anterior; la
revisión independiente nueva corresponde al pipeline. Si una revisión pendiente
antigua usó supervisor compartido, se bloquea para reconciliar y no se la etiqueta
retroactivamente como independiente. Un plan antiguo guardado puede recuperarse
sin volver a inferir. Nuevos proyectos usan planner/executor/reviewer.

Nuevo demo en runtime/phase3a1, sin modificar proyectos anteriores. Reapertura del
demo completo: cinco operaciones y dos checkpoints, cero turnos nuevos.
Evidencia curada: 58 archivos con manifiesto SHA-256. Sin operaciones n8n,
publicaciones, servicios externos de negocio ni efectos sobre producción.

## G. Repositorio

Rama codex/pello-phase3a1. HEAD inicial d25363a0141f720ada94dce0ee1162889711b759.
Primer commit 5966281; segundo commit incluye correcciones del incremento 2,
evidencia y este informe. La entrega final identifica su HEAD completo.

Se preservó e incorporó la adición canónica preexistente de README. AGENTS.md y
PELLO_V1_PRODUCT_SPEC.md se añaden explícitamente a Git, sin cambiar sus bytes.
El ZIP, INFORME-ARQUITECTURA-FASE2.md y paquete-contexto-arquitectura-fase2 siguen
sin seguimiento y sin modificaciones; no se stagean. No se versionan bases,
credenciales ni scratch de las copias de prueba. Los documentos operativos se
alinean y los contratos/evidencias históricos quedan marcados como históricos.

## H. Preparación para 3B

**Sí para comenzar la Fase 3B acotada**, con una nueva instrucción y comenzando
por capacidades/permisos del MCP oficial desde el perfil ejecutor. Antes de
escrituras: alcance y efectos autorizados, límites de operaciones, STOP y
reconciliación proporcional. La disponibilidad n8n no se comprobó en esta fase.

No hay bloqueador correctivo de 3A.1 pendiente. Las funcionalidades futuras
—decomposición autónoma, correo, continuidad prolongada, recuperación remota—
siguen fuera del alcance; no se presentan como defectos del incremento terminado.
La ruta legacy start/codex mantiene sus restricciones históricas distintas y
queda fuera del piloto: al habilitar recursos externos se debe verificar que
no exista un camino alternativo con privilegios equivalentes que eluda MCP.

**Fase 3B no iniciada.**
