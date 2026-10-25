# Fase 3B — contrato y límites

Fuente: PELLO_V1_PRODUCT_SPEC.md y las correcciones del usuario del 24-10-2026.
Una instancia: https://n8n-production-3374.up.railway.app; servidor OAuth global
llamado n8n. No renombrar ni reconfigurar autenticación. No crear infraestructura.
No modificar, ejecutar ni publicar dFoCUpXVrP9gc9rY o I4qwL8MuXvTotZKU.

## 3B-0: preflight de lectura

Comprobar desde el worker SDK existente conexión, OAuth, catálogo y lectura de
metadatos QA. Planner/Reviewer sin MCP; otras conexiones deshabilitadas.
Registrar herramientas, permisos observables y limitaciones, sin secretos.
Tests de perfil/propagación y regresión, revisión independiente y checkpoint.

## 3B-1: operaciones controladas

Python Core autoriza argumentos y registra intención antes de enviar cada
mutación mediante el RPC MCP nativo del SDK, en contexto ejecutor acotado.
No otro servidor/proxy/API REST administrativa. Diario SQLite, IDs inmediatos,
límites, STOP externo al agente y reconciliación por lectura, sin reintentos ciegos.

## 3B-2: un workflow QA nuevo

Planner define contrato; Tester prepara suites protegidas; Coder genera artefacto;
Core valida alcance/estructura antes de crear por MCP. Sin credenciales, clientes,
mensajes, scheduler ni integración comercial. Leer recurso creado y verificar
configuración real. Reviewer independiente; guardar export/checkpoint.

## 3B-3: publicación y ejecución

Solo ID del proyecto, versión revisada, pruebas previas aprobadas y límites/STOP.
Publicar por MCP; probar endpoint publicado con datos sintéticos y comparar con
contrato; consultar ejecuciones si la conexión lo permite. Preservar estados,
IDs y evidencia. Al entregar señalar retiro manual de MCP sin despublicar.

Cada incremento requiere tests, revisión y commit antes del siguiente. Un turno
SDK no equivale a una llamada MCP; se registran por separado. Mocks no acreditan
integración real. No avanzar más allá de esta fase.
