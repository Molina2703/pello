# Fase 3B-0 — preflight aprobado

24-10-2026, America/Bogota. READY para el siguiente incremento local; todavía
sin mutaciones n8n. SDK 0.163.0, servidor global n8n y endpoint oficial del
proyecto preparado. El worker retenido de Pello confirmó OAuth y runtime connected,
descubrió creación/validación/modificación/publicación/ejecución y consultó
search_workflows con query PELLO-3B-: cero resultados. No workflows HMP accedidos.

El servidor MCP anuncia versión 1.2.0; eso no verifica la versión de aplicación
n8n 2.44.6 informada por el usuario. Las herramientas de escritura están en el
catálogo, pero su ejecución efectiva queda pendiente de los incrementos siguientes.

Core usa el RPC MCP nativo del SDK en contexto ejecutor sin inferencia. Los
modelos Planner/Reviewer conservan todos los MCP deshabilitados; el perfil
ejecutor habilita solo n8n y, para llamadas de lectura, únicamente la herramienta
solicitada. Sin API REST administrativa ni proxy. El acceso global no se renombra.

Tests: 4 dirigidos PASS, incluyendo validación del nombre RPC contra el protocolo
instalado; 91/91 locales PASS (87 anteriores). Una llamada inicial fue rechazada
por un nombre RPC incorrecto; se preservó y corrigió según el esquema instalado.
Solo se repitieron lecturas, nunca mutaciones.

Reviewer SDK independiente: gpt-6.1-sol/high, PASS, hilo
01a17083-f2cc-7ce1-b467-c75639408e4c. Ver evidence/phase3b/reviews/3B0/review.json.
Evidencias nativas: evidence/phase3b/preflight/; referencias SDK oficiales obtenidas
por las mismas herramientas. Contrato y límites de fase: PHASE3B.md.
