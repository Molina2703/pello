# Pello — pipeline incremental, Fase 3A

`pipeline` extiende la instalación; `supervised` mantiene el flujo Fase 2 y sus
tres turnos. Los datos históricos no se sustituyen.

```powershell
.\pello.cmd pipeline --spec examples\quotes\SPEC.md --suite examples\quotes\acceptance --manifest examples\quotes\increments.json --policy examples\quotes\live-policy.json
.\pello.cmd pipeline --status PROJECT_ID
.\pello.cmd pipeline --resume PROJECT_ID
```

El primer comando consume cuota real. El demo tiene cinco llamadas máximas y un
intento por incremento. No repetir demos bloqueados automáticamente. Consultar
o reabrir un proyecto terminado no hace inferencia. `--stop-after 1` pausa tras un
checkpoint seguro; `--resume` continúa desde allí. Bloqueos requieren reconciliación.

El manifiesto del dueño fija especificaciones, inputs/outputs, componentes,
dependencias, criterios, suites y conteos. La IA añade un plan global e instrucciones;
no cambia esos contratos. Descomposición completamente autónoma desde una ficha
amplia y diseño de pruebas por IA siguen pendientes.

Estados de intento: PENDING → EXECUTED → VERIFYING → VERIFIED → REVIEWED → APPROVED; fallo →
FAILED → otro intento acotado. Los dependientes esperan aprobación y checkpoint.
El Tester es determinista. El Reviewer usa el supervisor read-only y recibe fuente,
diff y tests reales. Política every_increment o final; riesgo alto siempre se revisa.
Un fallo unittest aporta reproducción/traceback al Coder sin otra llamada solo para
diagnosticar. Infraestructura/especificación/integración inciertas bloquean para
reconciliación/replan; no hay replanteamiento automático del contrato del dueño.

Se reutilizan SQLite, pello_projects/tasks/sessions, SupervisedCycle._turn/_session,
worker retenido y runner unittest. Tablas pello_pipeline_* conservan contratos,
plan, intentos, intercambios, operaciones y checkpoints. Un lock de OS protege el
escritor y se libera tras muerte del proceso. Un resultado SDK guardado permite
reconciliar sin otra llamada; efectos inciertos bloquean. Checkpoints guardan
intención PREPARED antes de Git y reconocen solo el commit/padre/fuente esperados.
No hay garantía de ejecución remota exactamente una vez ni rollback destructivo.

Se ejecuta la suite del incremento y las de todos los ya aprobados. Hashes fijados,
conteo exacto y cero fallos/omisiones son obligatorios. Solo se permiten cambios a
componentes declarados. Python observa cambios independientemente del agente.

Política por defecto: max_attempts=2, max_turns=12, review=every_increment. Son límites
configurables; fallo repetido sin cambio observable detiene antes. Luna rutinario,
Sol configurado para alto riesgo o intentos posteriores; validación de catálogo,
esfuerzo y cuota observable, modelo enviado por turno y elección registrada. Sin
Astra, sustitución silenciosa ni API facturada. Cuota desconocida no es ilimitada.
Se consulta al iniciar/reanudar y un error de cuota durante un turno también bloquea.

`tools` declara referencias connection:/vault:/envref:, operaciones, entorno,
recursos, límites y método de verificación, sin credenciales. Solo Python/Git local
se habilitan en esta fase. MCP deshabilitado es un perfil de demo, no política final.
El próximo adaptador n8n requiere instancia DEV autorizada y reconciliación real.

Informes: runtime/supervised/PROJECT_ID/pipeline-report.json y .md. Los criterios
reportados son los cubiertos por suites aprobadas, no una auditoría individual.
Python -I/hashes/timeout no son sandbox fuerte de OS. Recovery entre incrementos se
prueba con respuestas inyectadas; rotación y caída real de turno remoto son otras
validaciones pendientes. Ver reports/PHASE3A.md para resultados medidos.
