# PELLO — PHASE 3B.3 COMPLETION REPORT

Estado de preparación: **PARTIAL — ventana temporal agotada**.
Este informe se actualizará con la aceptación real cuando exista autorización
temporal vigente. La publicación indicada abajo es real; HTTP permanece sin ejecutar.

## A. Executive Verdict

El workflow existente fue publicado por Pello mediante su SDK y MCP oficial.
Una lectura independiente del resultado confirmó active=true y la versión
851d73e4-0eb3-4f54-b51f-6c9a8fc89bf7. No se creó otro workflow.

El Reviewer de producto A respondió BLOCKED por una contradicción en los
metadatos de etapa: recibió suite published/1, que requiere los cuatro HTTP de B,
aunque debía revisar solo publicación y regresión del borrador. El código de
contexto se corrigió; el dictamen original y la aceptación final se conservan.
La nueva revisión A y las pruebas HTTP están pendientes de una ventana vigente.

## B. Budget Reconciliation

| Recurso | Inicial / autorización | Consumo actual |
|---|---|---|
| Mutaciones MCP | 6 originales + 8 autorizadas = máximo 14 | 7; quedan 7 |
| Llamadas MCP | Máximo 40, sin ampliación | 20; quedan 20 |
| POST sintéticos | Máximo independiente 4 | 0; quedan 4 |
| Turnos del proyecto | Máximo 10, sin ampliación | 8; quedan 2 |
| Workflows nuevos en este cierre | 0 autorizados | 0 |
| Operaciones de clientes / HMP | 0 autorizadas | 0 |

La autorización se registró de forma aditiva en pello_n8n_authorizations. No se
reiniciaron contadores ni se alteraron las 17 operaciones anteriores. El plazo
original había vencido; se aplicó una única extensión de 90 minutos que terminó
el 25-10-2026 a las 04:09:23 UTC, equivalente al 24-10-2026 a las 23:09:23 Bogotá.
No se concedió otra extensión automáticamente. Ver authorization-applied.json.

Los turnos del proyecto contabilizan sus llamadas Planner/Coder/Reviewer en la
tabla pello_pipeline_operations. Las revisiones de ingeniería del código de Pello
se registran por separado; no se presentan como turnos del producto QA.

## C. MCP Publishing Evidence

- Proyecto: phase3b-qa-first.
- Workflow: Tbuvwcxde8MEMYcJ.
- Nombre: PELLO-3B-MCP-INTEGRATION-QA-bb491b32d40943d5ad8a.
- Versión revisada, solicitada y observada activa: 851d73e4-0eb3-4f54-b51f-6c9a8fc89bf7.
- Operación persistida: phase3b-qa-first / publish, estado CONFIRMED.
- Lectura previa: publish-preflight-0, active=false.
- Lectura posterior: publish-observe-0-0, active=true y activeVersionId correcto.
- Graph/hash/credenciales comparados con el artefacto revisado y checkpoint
  8df481210e7a2692fdefe58a2851ee7ae51204ff.
- Tres nodos, sin referencias a credenciales ni efectos comerciales.
- Transporte: worker existente de Codex SDK, servidor n8n, RPC MCP nativo.

La revisión A todavía no está aprobada; no se afirma un checkpoint de aceptación
A mientras ese dictamen siga pendiente. Las respuestas reales están en
runtime/phase3b/supervised/phase3b-qa-first/evidence/mcp/ y el diario SQLite.

## D. HTTP Test Results

Endpoint autorizado:
https://n8n-production-3374.up.railway.app/webhook/pello-3b-bb491b32d40943d5ad8a

| Test | HTTP esperado | Respuesta esperada | Actual / ejecución | Estado |
|---|---|---|---|---|
| valid: 21 | 200 | request_id pello-3b-valid, status ok, result 42 | Sin ejecutar | PENDING |
| invalid-type: not-a-number | 400 | request_id pello-3b-invalid, status invalid, error invalid_input | Sin ejecutar | PENDING |
| negative: -3 | 200 | request_id pello-3b-negative, status ok, result -6 | Sin ejecutar | PENDING |
| repeat-valid: 21 | 200 | Igual al primer válido | Sin ejecutar | PENDING |

El plan conserva intencionalmente el mismo payload en los dos válidos. La
correlación se ordena por startedAt para asociar primero y repetición, aunque
n8n liste primero los más recientes. No se debilitaron expectativas ni se
hicieron solicitudes de prueba fuera de las cuatro permitidas.

## E. Failure and Repair History

Se conservaron RED/FAIL de las pruebas locales: duplicación del intercambio de
ejecución al reanudar, directorio de evidencia faltante, reconciliación en el
límite de mutaciones y recuperación desde BLOCKED tras una respuesta perdida.
Las correcciones se limitaron al harness/Core; no cambiaron el workflow.

Dos revisiones de ingeniería detectaron fallos de recuperación y se corrigieron.
La revisión posterior aprobó ese código. La revisión de producto A encontró el
conflicto de metadatos de suite descrito en A. Otra revisión de ingeniería pidió
el resultado completo de la regresión actual antes de cerrar. La revisión final
de ingeniería 3B3-closeout-A-ready recibió 126/126 y emitió PASS. Se conservan
todos los dictámenes anteriores y sus fuentes. No se transforma un BLOCKED en
PASS mediante narrativa.

Durante este cierre no se observó un fallo de implementación del workflow.
El Coder del producto usó Luna Medium para el artefacto JSON de publicación.
No hubo escalada del Coder. Reviewer de producto e ingeniería usan Sol High por
su responsabilidad de revisar cambios y evidencia de publicación independiente.

## F. Model Policy Clarification

Implementado: los perfiles iniciales Luna Low/Medium/High son configurables;
un número de intento ya no escala automáticamente a Sol. Se conservan catálogo,
permisos, presupuestos y registros anteriores, incluida la escalada histórica.
La corrección del contexto reutiliza el artefacto existente del Coder y el mismo
perfil del Reviewer; no atribuye al Coder un defecto de planificación de etapa.

Guía aprobada: Planner selecciona modelo/esfuerzo según complejidad, riesgo,
contexto y progreso; Reviewer aporta diagnóstico/evidencia; Core valida y registra.
Sol y su esfuerzo requieren justificación. Una decisión dinámica tipada del
Planner todavía necesita un futuro incremento acotado y no se presume implementada.
No se modificó la especificación maestra.

## G. Regression and Preservation

Baseline recibido: 118/118. Regresión de ingeniería previa a las últimas
correcciones: 123/123; posteriormente 125/125. La regresión final con el caso
cronológico adicional pasó **126/126**, sin skips. Pruebas de cierre específicas
verifican autorización idempotente, publicación sin repetir, pérdida de respuesta,
reanudación, contexto de revisión y protección de la suite final.

La suite protegida DRAFT pasó 5/5 antes de la publicación real. La suite publicada
y regresión del producto siguen obligatorias en B. STOP y presupuestos continúan
enforced; no se reintentan POST inciertos. Las operaciones HMP no se tocaron.
Se auditaron sin diferencias 773 archivos previos, 506 archivos de evidencia 3B,
las 17 operaciones MCP originales, los seis turnos originales y el checkpoint
anterior. Configuración global y sección n8n idénticas al inicio de este cierre.
Ver preservation-pre-delivery.json y snapshot closeout-published-pending.

## H. Repository State

Rama: codex/pello-phase3b. HEAD inicial:
4d7567463b66606dbf9b21b2f9da364706a63d4d.
Los cambios preparados se guardarán con evidencia de tests/revisión; los
checkpoints de aceptación A y B se registrarán después de sus gates reales.
Los tres elementos ajenos preexistentes permanecen fuera del staging.

## I. V1.3 Coverage Update

| Criterio | Estado actual en este QA |
|---|---|
| V1-07 | VERIFIED: creación/modificación real anterior, preservadas |
| V1-08 | Publicación real y versión activa confirmadas; revisión de etapa pendiente |
| V1-09 | PARTIAL: ejecución manual previa; HTTP publicado pendiente |
| V1-11 | PARTIAL: versiones/export/Git; restauración no demostrada |
| V1-13 | PARTIAL: no repetición y reconciliación de publicación con mocks; diario real preservado |
| V1-16 | Respeto del servidor oficial, ID propio, roles y ausencia de API administrativa |
| V1-23 | PARTIAL: entrega operativa y retiro de exposición MCP pendientes |

## J. Next Phase Recommendation

Primero cerrar los gates A/B pendientes. Después conviene un incremento pequeño
que convierta una especificación natural en contrato e incrementos con tests
protegidos, reduciendo el manifiesto manual actual y registrando la justificación
de modelo/esfuerzo. Mantener la cadena plan -> contrato -> tests -> código ->
revisión -> corrección -> entrega verificada. No se inició Phase 3C.
