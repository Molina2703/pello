# Pello — plan vigente hacia V1.3

La fuente de producto es [PELLO_V1_PRODUCT_SPEC.md](PELLO_V1_PRODUCT_SPEC.md).
Fase 3A.1 corrige verificación, separa Reviewer y configura modelos por rol.
Ver contrato/evidencia en [PHASE3A1.md](PHASE3A1.md). La demostración histórica
3A se conserva en reports/PHASE3A.md y evidence/phase3a/.

## Próxima fase propuesta: 3B, piloto vertical por MCP oficial

Solo mediante una nueva instrucción del usuario. Una instancia primaria n8n
Railway, conexión al MCP oficial configurada manualmente en config.toml.
Reutilizar herramientas conectadas; sin proxy propio, segunda instancia DEV,
duplicados por ambiente ni acceso administrativo alternativo que eluda MCP.

1. Comprobar desde el proceso SDK herramientas, permisos y capacidades reales.
   Si falta una operación, registrar el bloqueo; no introducir otra vía automáticamente.
2. Workflow QA autorizado: crear/modificar, registrar ID automáticamente, preservar
   configuración/versión no secreta, revisar, publicar y verificar estado/ejecución.
   Publicación autónoma dentro del alcance y efectos inicialmente autorizados.
3. Probar el mecanismo real requerido, incluidos webhooks publicados cuando
   corresponda, con recursos controlados; comprobar credenciales adjuntas.
4. Registrar intención, ID, respuesta y evidencia. Reconciliar por lectura o
   bloquear resultados inciertos antes de repetir. Aplicar presupuestos, STOP
   y aislamiento proporcionales al piloto antes de habilitar efectos externos.
5. Respetar Available in MCP. Al entregar, identificar workflows listos para
   retirar acceso MCP; deben seguir publicados y operativos.

No basta exportar JSON ni pasar tests locales para afirmar integración real.
No contactar clientes ni producir efectos fuera del alcance.

## Hitos posteriores

- Requisitos estables desde lenguaje natural, validación de ambigüedades,
  incrementos/contratos y pruebas independientes antes del Coder.
- Reparación y escalada demostradas mediante SDK real; los mocks no bastan.
- Servicio auxiliar, restauración y registro/limpieza autorizada de datos QA.
- Rotación y reconstrucción de contexto, recuperación real, STOP y operación
  prolongada en Windows mientras haya recursos y autenticación.
- Progreso por requisitos, programación de reportes y correo autorizado.
- Aceptación final de negocio según §13.1, entrega y ciclo de acceso MCP.

## Política habitual y adaptación

Planner Sol High; Coder Luna Medium; Reviewer Sol High; Tester determinista o
variable cuando necesite IA. Configuración explícita, disponibilidad comprobada,
escalada por evidencia y registro de resultados. El 70–80% es una pauta flexible
por responsabilidad, no cuota de modelos económicos, tokens o costes.
No requiere API de pago ni Reviewer ChatGPT externo.
