# Pello — plan de implementación

## Entrega actual: Fase 3A

Completada: dos incrementos reales, cinco turnos Luna/low y 69 tests locales
aprobados; siguiente hito no iniciado.

Pipeline secuencial sobre Fase 2: plan global, incrementos dependientes,
intentos/exchanges, suites externas, revisión por política, checkpoints y
reanudación. Demostración real pequeña tras tests deterministas, sin repetir
automáticamente un demo bloqueado. Estado medido: reports/PHASE3A.md y STATE.md.

## Próximo hito: n8n DEV y diario de operaciones externas

Sobre la configuración por proyecto implementada, crear un adaptador mínimo
MCP/API para una instancia n8n DEV explícitamente autorizada. Inspeccionar versión
y capacidades, resolver referencias seguras de conexión y aplicar allowlist de
operaciones/recursos. Persistir intención, IDs remotos y resultado, utilizar
idempotencia cuando exista y reconciliar por lectura antes de repetir una
escritura incierta. No basta un archivo JSON ni una prueba exclusivamente Python.

## Hitos que faltan para la V1

1. **Integración vertical DEV y reparación:** crear/modificar un workflow ficticio
   en la instancia autorizada, ejecutar escenarios y guardar evidencia de IDs,
   inputs/outputs, fallos y correcciones. Conectar verificadores remotos al pipeline.
2. **Aislamiento:** usuario restringido, VM/contenedor y límites de red/filesystem/
   procesos antes de código no confiable o credenciales de mayor alcance. El
   perfil actual no es sandbox de OS fuerte.
3. **Memoria/versionado y rotación:** construir contexto por rol desde plan,
   decisiones, checkpoints y estado remoto confirmado. Registrar linaje, política
   de rotación y conflictos de escritor. Verificar continuación sin repetir trabajo.
4. **Operación desatendida:** ampliar recuperación local a turnos SDK interrumpidos,
   cuota, reinicios Windows y cancelación/reconciliación. Después, launcher local
   supervisado; no requiere cloud de Pello ni promete 24/7.
5. **Reporte diario y correo:** separar implementación, criterios cubiertos,
   integración, bloqueos y consumo. Scheduler local y outbox idempotente con envío
   simulado primero; correo real solo desde un buzón autorizado.
6. **Aceptación V1 de negocio:** otra ficha realista, infraestructura DEV autorizada,
   recurso realmente desplegado, pruebas externas, reparación, cambio de sesión y
   reinicio. Entrega documentada y aprobación final humana.

La descomposición autónoma de fichas amplias y pruebas asistidas por IA se
evaluarán contra el manifiesto escrito por el dueño que usa este prototipo.
Medir overhead de incrementos y routing Luna/Sol: 70–80% económico es hipótesis,
no porcentaje obligatorio. Reviewer ChatGPT futuro es opcional, no dependencia.
