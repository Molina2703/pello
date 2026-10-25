# Fase 3B-1 — operaciones controladas aprobadas

Diario SQLite aditivo por proyecto, intención/argumentos no secretos, hash,
estados IN_FLIGHT/SUBMITTED/CONFIRMED/FAILED/UNCERTAIN y evidencia. El worker
reclama la operación atómicamente y persiste el ID remoto antes de responder.
Respuestas confirmadas se reutilizan; escrituras inciertas bloquean otras
mutaciones y solo se reconcilian por búsqueda del nombre QA único.

Solo ID del proyecto; ambos workflows HMP prohibidos. Lecturas de recursos exigen
prueba del proyecto y workflowId propio; las ejecuciones además deben haber sido
observadas en ejecutar/listar ese workflow. Planner/Reviewer sin MCP. Solo Core
invoca mutaciones nativas; esos contextos no ejecutan modelos. Presupuestos
inmutables por proyecto, plazo persistido y archivo STOP independiente del agente.
STOP no llama a despublicar ni modifica workflows entregados.

Pruebas: RED inicial sin módulo; regresión específica RED con seis fallos por
lecturas sin pertenencia; corrección y suite completa **102/102 PASS**. También
se probó lectura positiva de ejecución propia, límites, secretos, timeout,
ambigüedad, publicación sin revisión y guardado de ID antes de regresar al Core.
Las respuestas remotas de esos tests son inyectadas, no prueba n8n real.

La revisión independiente detectó el hueco de lectura y emitió FAIL; se conserva
sin reinterpretarlo. La revisión inicial también recibió un tail de regresión
incompleto: el helper ahora impide iniciar cierre sin log terminado. Revisión
final corregida: Sol High, PASS, hilo 01a17095-4b30-7d61-94fb-6603a2e61ece.
Evidencia: evidence/phase3b/reviews/3B1-fixed/review.json y 3b1-fixed-all-tests.log.

**Ninguna mutación real n8n realizada.** Los límites de definición segura,
pipeline QA y publicación funcional se implementan en 3B-2/3; no se los declara
completos por los mocks de este incremento.
