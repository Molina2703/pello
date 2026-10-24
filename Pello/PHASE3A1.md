# Fase 3A.1 — contrato de ejecución

Objetivo: corregir la aceptación de bytecode obsoleto y alinear revisión,
modelos y documentos con PELLO_V1_PRODUCT_SPEC.md, sin integrar n8n.

## Incremento 1: fuente actual

Modificar el verificador común, conservando gates, hashes y restricciones.
Aceptar únicamente el comportamiento del fuente actual: caché con 7/fuente
con 9 falla; fuente con 7 pasa. Fallos impiden aprobación, checkpoint y ejecución
de dependientes. No borrar cachés del workspace original. Verificar 69 regresiones
y aceptación histórica limpia de Fase 2/3A; revisar y guardar commit antes de seguir.

## Incremento 2: alineación

Reviewer con identidad/contexto persistente separado y solo lectura; conservar
sesiones anteriores. Perfiles configurables Planner Sol High, Coder Luna Medium,
Reviewer Sol High y Tester variable, con escalada y validación sin sustitución.
Actualizar planificación operativa y versionar especificación/AGENTS sin alterar
la especificación ni evidencia histórica. Probar migración, resume, contexto,
permisos, modelos y regresiones. Demo SDK local pequeño si hay recursos.

Los backends inyectados son evidencia local, no SDK real. No n8n, publicaciones,
servicios de negocio, correo, scheduler, descomposición autónoma ni rediseño.

## Operación actual

El pipeline crea hilos planner, executor y reviewer distintos en un solo worker
SDK retenido. Tester sigue siendo Python determinista; su perfil IA es opcional.
Reviewer recibe ficha, contrato, restricciones, dependencias aprobadas, fuente,
diff y resultados objetivos; no recibe reasoning_summary ni narrativa del Coder.

La migración v4 conserva cada fila supervisor/executor y amplía roles de sesión
en una transacción. Los proyectos completos históricos no vuelven a invocarse;
un resultado review antiguo compartido no se presenta como revisión independiente.
Si se intenta recuperar ese resultado pendiente, se bloquea para reconciliación.

PipelinePolicy() usa Planner Sol High, Coder Luna Medium, Reviewer Sol High;
role_profiles permite configurarlos. Una política anterior con campos explícitos
routine/advanced conserva su routing original al no declarar role_profiles.
El Coder puede escalar al perfil advanced por riesgo o intento. No hay cuota 70–80%.

Ejemplo local acotado (cinco turnos, un intento por incremento; consume cuota):

```powershell
.\pello.cmd --root runtime\phase3a1 pipeline --spec examples\quotes\SPEC.md --suite examples\quotes\acceptance --manifest examples\quotes\increments.json --policy examples\quotes\phase3a1-policy.json --project-id phase3a1-quotes-first --timeout 240
```

MCP, plugins, red de herramientas y API facturada continúan deshabilitados para
estos roles. No repetir automáticamente un demo bloqueado. La configuración de
n8n y sus operaciones pertenecen a una fase posterior autorizada.
