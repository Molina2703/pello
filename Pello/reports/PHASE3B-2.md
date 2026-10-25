# Fase 3B-2 — borrador real aprobado

Implementación localizada: n8n_pipeline.py extiende IncrementalPipeline;
n8n_qa.py verifica el contrato y n8n_expression.py limita su sintaxis.
CLI n8n-pilot. Planner define contrato antes de las suites protegidas y Coder.
Core convierte el JSON del Coder a Workflow SDK y llama al MCP nativo mediante
el worker existente. No inferencia en los contextos de transporte MCP.

Pruebas locales: 112/112 PASS, 25 específicas. Las revisiones de ingeniería
detectaron y bloquearon: resultados intermedios sin éxito terminal, parámetros
extra no revisados, ID remoto distinto y escape por constructor en el evaluador.
Se conservan FAIL y pruebas RED; parser estricto y VM sin objetos del anfitrión.
Revisión final de ingeniería 3B2-safe: Sol High, PASS.

Demostración REAL, proyecto phase3b-qa-first:

- Workflow Tbuvwcxde8MEMYcJ.
- Nombre PELLO-3B-MCP-INTEGRATION-QA-bb491b32d40943d5ad8a.
- Webhook -> Edit Fields -> Respond to Webhook, sin credenciales ni otros efectos.
- Validación oficial aprobada y Available in MCP confirmado.
- Primer borrador: ejecuciones 3 y 4 correctas; Reviewer FAIL por guard del cuerpo vacío.
- Coder corrigió automáticamente el mismo recurso; no segunda creación.
- Versión revisada 851d73e4-0eb3-4f54-b51f-6c9a8fc89bf7.
- Ejecuciones 5 y 6 correctas, 5/5 tests protegidos, Reviewer PASS.
- Checkpoint del producto 8df481210e7a2692fdefe58a2851ee7ae51204ff.
- Tres sesiones independientes persistentes y seis turnos SDK reales.
- 17 llamadas MCP confirmadas: una creación, una actualización y cuatro ejecuciones.
- Estado PAUSED tras un incremento; workflow SIN PUBLICAR.

El ciclo de reparación acotada se observó en este caso concreto. No demuestra
reparación general de integraciones. La corrección de ingeniería previa fue
trabajo del agente de desarrollo, no una ejecución autónoma del producto.

Limitación observada: las seis mutaciones agotan el presupuesto persistido
max_mutations=6; publicar necesita otra mutación. No se amplió el límite.
3B-3 debe respetar este bloqueo; la integración publicada permanece pendiente.

Evidencia inmutable: evidence/phase3b/live-draft/ (161 archivos, estado SQLite
exportado, fuentes, respuestas SDK/MCP, verificaciones, revisiones y hashes).
Históricos: 773 archivos y config.toml sin cambios según auditoría de hashes.
