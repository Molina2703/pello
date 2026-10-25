# Publicación concreta pendiente de presupuesto

Proyecto: phase3b-qa-first. Recurso único: Tbuvwcxde8MEMYcJ.
Nombre: PELLO-3B-MCP-INTEGRATION-QA-bb491b32d40943d5ad8a.
Versión aprobada: 851d73e4-0eb3-4f54-b51f-6c9a8fc89bf7.
Checkpoint de producto: 8df481210e7a2692fdefe58a2851ee7ae51204ff.

## Acción preparada

1. Coder prepara publication.json para ese ID y versión, sin modificar el workflow.
2. Core verifica ID, versión, hash de configuración, nodos, credenciales y checkpoint.
3. Una llamada nativa publish_workflow con workflowId y versionId exactos.
4. Lectura confirma active=true y activeVersionId igual a la versión aprobada.
5. Cuatro POST de QA al único endpoint:
   https://n8n-production-3374.up.railway.app/webhook/pello-3b-bb491b32d40943d5ad8a
6. Casos: 21 -> 42/200; texto -> invalid_input/400; -3 -> -6/200;
   repetir 21 -> 42/200. IDs sintéticos pello-3b-*.
7. MCP consulta solo ejecuciones de ese workflow y relaciona cuatro IDs distintos
   con las entradas y salidas. Lectura final verifica publicación sin cambios.
8. Suite protegida y regresión del borrador; Reviewer independiente; checkpoint.

Ningún mensaje, cliente, credencial, scheduler ni otro workflow. HTTP sin
redirecciones, proxies ni API administrativa. Cuatro POST como máximo;
intención persistida antes del envío, incertidumbre bloquea repeticiones.
Los contextos nativos MCP usan el SDK existente y no ejecutan inferencia.

## Bloqueo actual

Presupuesto local fijado por el agente: 6 mutaciones MCP. Consumo confirmado:
crear (1), ejecutar primer borrador (2), corregir parámetros (1), ejecutar
borrador corregido (2). Total 6/6; llamadas MCP 17/40. El límite fue demasiado
ajustado para la reparación real. No es una denegación de permisos de n8n.

El prompt original, sección 10, ordena: “Never grant yourself more budget after
reaching a hard limit.” El código bloquea antes del Coder y de cualquier nueva
operación. No permite crear otro proyecto para eludir el límite.

Para completar esta acción hace falta autorización explícita del usuario para
una mutación MCP adicional (total 7), los cuatro POST ya descritos y una ventana
acotada de 20 minutos. Se conserva el mismo recurso, OAuth, conexión y límite
de 40 llamadas MCP. Sin esa excepción la fase se entrega PARTIAL y sin publicar.

## Estado de validación

Recorrido completo y fallos verificados con respuestas inyectadas, marcados
TESTED WITH MOCKS. La publicación y los POST reales permanecen pendientes.
El informe final debe distinguir este estado de los borradores MCP ya reales.
