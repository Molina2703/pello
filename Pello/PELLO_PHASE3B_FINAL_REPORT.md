# PELLO — PHASE 3B FINAL REPORT

Fecha: 24 de octubre de 2026, America/Bogota. Fuentes: especificación V1.3,
prompt Phase 3B y correcciones del entorno entregadas por el usuario.

## A. Executive Result

**PARTIAL.** La integración oficial n8n funciona dentro del pipeline real de
Pello: contrato y plan, Coder, validación, creación, ID persistido, ejecución,
revisión independiente, corrección acotada y checkpoint. Se creó exactamente
un workflow, sin credenciales ni efectos comerciales. Está **sin publicar**.

La publicación y las pruebas HTTP reales no están verificadas. El bloqueo es
el presupuesto local de seis mutaciones, fijado por el agente y agotado durante
la reparación del borrador. Fue demasiado ajustado; no se atribuye este bloqueo
a n8n, OAuth ni permisos. El prompt prohíbe ampliar límites al agotarlos.

El soporte de publicación está preparado y probado con simulaciones. La acción
concreta y el presupuesto adicional necesario están en
`reports/PHASE3B-PUBLICATION-PLAN.md`. La fase V1 completa sigue pendiente.

## B. MCP Preflight

- Python 3.12.6, SDK oficial openai-codex 0.163.0, Git y SQLite existentes.
- Servidor global `n8n`, OAuth, endpoint
  https://n8n-production-3374.up.railway.app/mcp-server/http.
- El worker retenido del SDK confirmó conexión y consultas reales. No se usó
  el conector n8n interactivo de ChatGPT ni una API administrativa alternativa.
- Catálogo real: create_workflow_from_code, validate_workflow, update_workflow,
  publish_workflow, execute_workflow, get_workflow_details,
  search_workflow_executions, get_workflow_execution y referencias del SDK.
  Inventario completo: `evidence/phase3b/preflight/inventory.json`.
- Permisos efectivos demostrados: buscar el nombre QA, crear, modificar el
  recurso propio y ejecutar/leer resultados. Publicación está en el catálogo;
  todavía no se ha demostrado su ejecución efectiva.
- El MCP anuncia versión de protocolo/servidor **1.2.0**. No acredita la versión
  de aplicación n8n **2.44.6** informada por el usuario; no se revalidó esa versión.
- Referencias oficiales consultadas: [conexión MCP](https://docs.n8n.io/connect/connect-to-n8n-mcp-server/)
  y [herramientas](https://docs.n8n.io/connect/connect-to-n8n-mcp-server/mcp-server-tools-reference/).

Decisión de arquitectura: el Coder produce JSON dentro de su workspace; Core
valida y convierte ese artefacto al Workflow SDK. El mismo worker de Pello
envía los RPC nativos `mcpServer/tool/call` mediante Codex SDK, en contextos
ejecutores efímeros sin inferencia, con una herramienta habilitada por operación.
No es un servidor MCP ni proxy nuevo. Planner/Reviewer mantienen MCP deshabilitado.
Las conversaciones de los modelos no pueden enviar mutaciones directamente.

## C. Increment Results

| Incremento | Resultado y pruebas | Revisión / checkpoint |
|---|---|---|
| 3B-0 | Preflight real de lectura; 4 tests específicos y 91 de regresión | Reviewer SDK PASS; ff5d54f304e73bb2698ee6e7aba5d019efddf637 |
| 3B-1 | Diario, pertenencia, IDs inmediatos, límites, STOP, incertidumbre; 102 tests | FAIL de lecturas sin alcance corregido; PASS final; 1f1055840c1da543dfec69a4d264e85949c3ee13 |
| 3B-2 | Workflow real y reparación acotada; 112 tests, 5 protegidos por intento | Ingeniería 3B2-safe PASS; Reviewer del producto FAIL/PASS; 9d0269d65c3d51747a307337260be26f6c775539 |
| 3B-3 | Código local de publicación y verificación; 118/118 tests; STOP y bloqueo real sin operaciones nuevas | Ingeniería 3B3 PASS; publicación real pendiente por presupuesto |

Archivos principales: `athis_autopilot/n8n_mcp.py`, `n8n_operations.py`,
`n8n_pipeline.py`, `n8n_qa.py`, `n8n_expression.py`, `n8n_http.py`, extensiones del
worker/SDKBackend/CLI y tests n8n. La arquitectura previa se conserva.

Las revisiones de ingeniería detectaron resultados intermedios aceptados sin
éxito terminal, parámetros extra, ID remoto incorrecto y escape del evaluador.
Se guardaron los FAIL y RED; se corrigieron antes de la primera creación real.
No se presenta ese trabajo del agente como reparación autónoma del producto.

La revisión real del producto detectó por inspección un guard incorrecto para
el cuerpo vacío. Pello activó un segundo intento, escaló el Coder de Luna Medium
a Sol High, actualizó el mismo recurso, repitió verificaciones y obtuvo PASS.
Esto demuestra ese ciclo acotado; el caso de cuerpo vacío no fue un fallo HTTP
observado y no acredita reparación general de integraciones.

## D. Real Workflow Evidence

- Proyecto: `phase3b-qa-first`.
- Instancia: https://n8n-production-3374.up.railway.app.
- Workflow ID: **Tbuvwcxde8MEMYcJ**.
- Nombre: `PELLO-3B-MCP-INTEGRATION-QA-bb491b32d40943d5ad8a`.
- Estructura: QA Webhook 2.2 -> QA Result / Edit Fields 3.5 -> QA Response 1.5.
- Tres nodos; credenciales ausentes en todos; sin otros workflows ni HTTP Request.
- Versión inicial: `367b9cfd-ecd5-4bad-a26c-3ca9a084b9db`.
- Versión corregida y revisada: `851d73e4-0eb3-4f54-b51f-6c9a8fc89bf7`.
- Validación oficial de ambas definiciones: valid=true. Available in MCP=true.
- Publicación observada al cierre del borrador: active=false, sin versión activa.
- Ejecuciones manuales iniciales 3 y 4; corregidas 5 y 6, éxito terminal y salida
  del nodo final confirmados mediante get_workflow_execution.

Entradas reales de las ejecuciones 5 y 6:

```json
{"request_id":"pello-3b-valid","value":21,"op":"double"}
{"request_id":"pello-3b-invalid","value":"not-a-number","op":"double"}
```

Salidas reales correspondientes:

```json
{"request_id":"pello-3b-valid","status":"ok","result":42}
{"request_id":"pello-3b-invalid","status":"invalid","error":"invalid_input"}
```

Esas ejecuciones son MCP/manual: no demuestran códigos HTTP del webhook publicado.
Los POST y las respuestas HTTP reales siguen **NOT RUN**. El endpoint preparado
es `/webhook/pello-3b-bb491b32d40943d5ad8a` en la instancia autorizada.

Evidencia: `evidence/phase3b/live-draft/`, incluyendo export de SQLite,
fuentes/contratos protegidos, RPC, resultados reales, verificaciones, revisiones
y SHA-256. Checkpoint del producto: `8df481210e7a2692fdefe58a2851ee7ae51204ff`.
Se conservaron seis turnos reales y tres sesiones independientes:

| Rol | Thread ID |
|---|---|
| Planner | 01a170b4-ceb1-7122-82bb-f57bc4d840a6 |
| Coder | 01a170b5-51ca-7922-a6d7-dc3069e29621 |
| Reviewer | 01a170b6-2c05-7bc1-a726-4f4943ba5212 |

## E. External Operation Safety

17 operaciones MCP confirmadas del proyecto; seis mutaciones: crear una vez,
actualizar una vez y ejecutar cuatro veces. Ninguna operación real incierta,
ninguna segunda creación. Lecturas y simulaciones no se cuentan como pruebas
de publicación. Límites persistidos: 40 llamadas MCP, 6 mutaciones, 10 turnos
de modelo, 2 intentos por incremento y plazo de una hora desde el proyecto.
El soporte HTTP añade un límite independiente de cuatro POST autorizados.

Las intenciones se guardan antes de enviar; el worker reclama atómicamente la
operación y persiste el ID antes de escribir la respuesta. Confirmaciones se
reutilizan. Timeout/resultado incierto bloquea escrituras y repeticiones; creación
solo se reconcilia por nombre único e ID propio. Ambigüedad sigue bloqueada.
Las recuperaciones de incertidumbre se probaron con simulaciones, no con un
timeout real provocado en n8n.

STOP se comprueba antes de cada nueva operación y al reanudar. No despublica
recursos entregados. Los modelos no pueden editar el archivo STOP externo.
También se ensayó STOP sobre este proyecto real y se retiró únicamente el marcador
creado para esa prueba. Luego dos reanudaciones quedaron bloqueadas por presupuesto:
antes y después, 17 operaciones MCP, 6 turnos y 0 POST. Evidencia:
`evidence/phase3b/3b3-real-stop-budget-resume.json`.
Solo se admite el ID propio; los HMP dFoCUpXVrP9gc9rY e I4qwL8MuXvTotZKU nunca
fueron leídos, modificados, ejecutados ni publicados en este piloto.

Se excluyen secretos en argumentos. Se filtra metadata interna de autenticación
y resumeToken antes de persistir nuevas respuestas. Los campos internos de cuatro
respuestas de ejecución de esta fase se redactaron también en sus exportaciones;
se conservan IDs, estados y resultados, y se regeneraron hashes. El checkpoint
local 3B-2 fue reemplazado antes de entrega para excluir esos valores de su árbol.
No hubo publicación de repositorio ni comandos para editar OAuth/configuración
global. La auditoría final detectó una huella distinta de config.toml, con marca
temporal coincidente con el primer contexto Coder. No puede atribuirse su causa
con el baseline disponible: se guardó hash inicial, no copia de secretos/config.
No se restauró ni sobrescribió el archivo. Se comprobó que `n8n` conserva nombre,
endpoint oficial y estado habilitado. Ver `config-change-audit.json`.

Único recurso creado: el workflow QA arriba indicado. Al terminar su desarrollo,
el usuario puede quitar **Available in MCP** solo para ese ID. Si se publica más
adelante, retirar exposición MCP debe conservar su publicación y operación.
Si deja de necesitarse, despublicar únicamente este QA es una decisión manual.
No apagar MCP global ni alterar los workflows HMP para la limpieza.

## F. Regression Results

Baseline anterior: 87 tests. Al cierre del borrador: 112/112. Implementación de
publicación: **118/118 PASS**, 31 nuevos frente al baseline; 6 específicos de
publicación. Sin fallos ni skips en la regresión final registrada.

Los tests cubren propagación SDK/MCP, roles, pertenencia, persistencia, retorno
temprano de ID, incertidumbre/reconciliación, STOP, presupuestos, sintaxis segura,
definición remota, resultado terminal, publicación exacta, cuatro POST simulados,
correlación de ejecuciones y reanudación sin efectos duplicados.

La suite protegida real del borrador ejecutó 5/5 en cada intento, incluyendo
nueve casos deterministas. La suite de publicación todavía no se ejecutó con
evidencia real. Los tests simulados no convierten esa ausencia en VERIFIED.
La auditoría de 773 archivos históricos permanece sin cambios. La huella global
de config.toml cambió durante la sesión; la conexión n8n conserva sus invariantes,
como se explica en E. No se afirma igualdad binaria de esa configuración.

## G. Repository State

Inicio: rama `codex/pello-phase3a1`, HEAD
`3c400b6f239c22f9ae9b5c02090ac057da1edb98`.
Rama de trabajo: `codex/pello-phase3b`. Los checkpoints de ingeniería están en C;
el HEAD de entrega se registra tras el checkpoint final, evitando autorreferencia.

Se excluyen del staging los tres elementos ajenos preexistentes:
`Pello-Contexto-Arquitectura-Fase2.zip`, `Pello/INFORME-ARQUITECTURA-FASE2.md` y
`Pello/paquete-contexto-arquitectura-fase2/`. No se modificaron SQLite ni evidencia
de las fases previas. Runtime nuevo separado: `Pello/runtime/phase3b/`.
Especificación maestra intacta; SHA-256:
`6bca1e0b8d871201601e83b6cdbeadb0554fa52be18a8d624a29ca46ca44674d`.

## H. V1.3 Coverage

| Criterio | Estado demostrado en este alcance QA |
|---|---|
| V1-07 | VERIFIED: crear y modificar workflow real por MCP oficial |
| V1-08 | PENDING: soporte local probado; publicación real bloqueada |
| V1-09 | PARTIAL: ejecuciones manuales reales; webhook publicado pendiente |
| V1-11 | PARTIAL: versiones, export y Git; restauración remota sin demostrar |
| V1-13 | PARTIAL: diario y no repetición; incertidumbre/reconciliación probadas con mocks |
| V1-16 | VERIFIED en el piloto: exposición MCP, ID propio, roles, sin vía administrativa alternativa |
| V1-23 | PARTIAL: ID y desarrollo MCP reales; retiro de exposición y entrega operativa pendientes |

No se declara Pello V1 completo ni se generaliza el piloto a workflows comerciales.

## I. Next Recommended Development Phase

Primero cerrar la publicación pendiente de 3B-3 con autorización del presupuesto
adicional concreto. Después conviene ampliar contratos de fallo, reconciliación
de publicación/ejecución y restauración de versiones con ensayos controlados,
además de validar entrega sin exposición MCP. No se inició ninguna fase posterior.
