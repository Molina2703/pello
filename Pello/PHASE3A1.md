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
