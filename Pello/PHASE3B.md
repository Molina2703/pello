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

## Cierre 3B-3 y aclaración de modelos aprobada el 24-10-2026

El usuario autoriza ocho mutaciones MCP adicionales, máximo acumulado 14,
solo para Tbuvwcxde8MEMYcJ; cuatro POST independientes; ningún workflow nuevo.
Si expira el plazo original, una única extensión de hasta 90 minutos. Core
registra el permiso y los valores anteriores/nuevos sin reiniciar contadores.
Incremento A publica y revisa la versión aprobada antes de pausar; B verifica
HTTP y ejecuciones, mantiene aceptación protegida y obtiene el checkpoint final.

Luna es la preferencia para programar. Low/Medium/High son elecciones iniciales
según complejidad, incertidumbre, contexto y riesgo; no una escalera obligatoria.
Un fallo ordinario no prueba incapacidad ni causa escalada por número de intentos.
Planner decide alcance y selección; Reviewer diagnostica y aporta evidencia de
progreso o necesidad de replantear/escalar. Core valida catálogo, permisos,
presupuestos y registra decisiones. Sol requiere evidencia o riesgo excepcional
justificado; su esfuerzo también es configurable. Tras resolverlo, volver a Luna
en incrementos ordinarios. El historial previo Luna Medium -> Sol High se conserva.

Implementado en este cierre: eliminación de escalada automática por contador y
perfiles iniciales configurables. La selección dinámica de modelo/esfuerzo
propuesta por Planner en un mensaje tipado, con justificación y aprobación de
Core, requiere un futuro incremento acotado; no se presume implementada aquí.
Para el artefacto PUBLISH ya planificado se conserva Luna Medium: JSON localizado,
contrato estable, sin cambios al workflow. Reviewer independiente usa Sol High.
