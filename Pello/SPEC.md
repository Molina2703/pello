# Pello V1 — contrato de producto

> Definición vigente: PELLO_V1_PRODUCT_SPEC.md (V1.3), PHASE3A1.md y PLAN.md.
> El texto siguiente es el contrato histórico de 3A. Sus decisiones DEV y
> aprobación general de activación están superadas: una instancia Railway,
> MCP oficial configurado por el usuario, Available in MCP y publicación
> autónoma dentro del alcance autorizado. Retirar MCP no despublica la entrega.

Pello es el ingeniero interno de desarrollo de software y automatización de
negocio de ATHIS GROUP. Su objetivo es convertir fichas aprobadas en soluciones
implementadas, integradas, probadas y documentadas con supervisión humana mínima.
El fundador define alcance, provisiona infraestructura, autoriza herramientas y
credenciales y aprueba activación final o acciones sensibles.

La V1 deberá ejecutar incrementos funcionales, verificar cada uno, corregir
fallos con límites e integrar recursos reales autorizados (incluido n8n cuando
proceda). Debe conservar memoria entre sesiones/reinicios, continuar en Windows
y enviar informes diarios por correo. Un workflow JSON local no es una integración.

## Alcance actual: Fase 3A

Ampliar la Fase 2 mediante un plan global persistente, incrementos dependientes,
intentos e intercambios correlacionados, pruebas independientes, revisión según
política, checkpoints Git y continuación secuencial. Demostración de dos incrementos
con datos ficticios. El dueño proporciona inicialmente contratos y suites; Python
controla avances y no permite aprobar pruebas fallidas ni debilitar criterios.

Modelos Luna/Sol disponibles y esfuerzos validados; Astra/API de pago prohibidos.
Límites configurables. Demo: hasta cinco turnos, un intento por incremento y ningún
reintento automático de una demostración bloqueada.

## Límites

Solo herramientas locales. Configuración por proyecto con referencias no secretas,
operaciones, entorno, recursos, límites y verificación. Herramientas externas
habilitadas se rechazan en Fase 3A. No producción, GUI, cloud de Pello, correo real
ni agentes en paralelo. Integración DEV, rotación, recuperación remota robusta y
reportes programados son hitos posteriores; V1 completa sigue pendiente.

La nueva solicitud prioriza pipeline incremental; la propuesta histórica de
rotación como siguiente Fase 3 queda sustituida. Se preservan informes anteriores:
instalación/Fase 1 con un smoke real de un turno; Fase 2 con plan/ejecución/revisión
reales en tres turnos, 12 pruebas de aceptación y 43 locales.
