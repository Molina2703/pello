# Engineering decisions — historical Phase 2

## Alineación vigente de Fase 3A.1

La fuente final es PELLO_V1_PRODUCT_SPEC.md. Aceptación desde copias limpias de
fuente/suites, sin bytecode previo; Reviewer en hilo distinto del Planner/Coder,
solo evidencia objetiva y lectura. Perfiles por rol configurables con validación
de catálogo y escalada; políticas históricas explícitas conservan sus valores.
La migración v4 preserva sesiones supervisor/executor y habilita nuevos roles.

PLAN.md sustituye el requisito n8n DEV y la interpretación económica del 70–80%.
Una instancia Railway, MCP oficial ya configurado y publicación autorizada sin
aprobaciones repetitivas; no proxy, duplicación por ambiente ni bypass administrativo.
Las decisiones históricas siguientes se conservan para interpretar la evidencia.

1. **Reuse the prototype.** `SupervisedCycle` extends the existing supervisor's
   SQLite lifecycle and Git initialization. Additive `pello_*` tables preserve
   legacy jobs/events. The existing SDK worker/adapter gains role, model, effort,
   schema and session-only options; no message broker or service is added.
2. **Python owns authority.** Pydantic rejects malformed/incomplete/mismatched
   exchanges and invalid plans. Tasks have IDs, sequential dependencies and
   completion criteria. Agent summaries remain claims; Python observes source
   changes and independent tests. Failed or unexecuted tests cannot be approved.
3. **Bounded durable operations.** Unique `plan`, `execute`, `review` reservations
   cap each project at three turns. Requests, responses, messages, task states
   and sessions persist. Completed output can be replayed locally; uncertain
   effects block. This is not an exactly-once/concurrent execution guarantee.
4. **Separate roles and permissions.** The roles must have distinct thread IDs.
   Supervisors request read-only access; executors request workspace writes.
   External tools and additional agents are disabled for nested roles only.
5. **Explicit economical configuration.** Actual catalog-confirmed `gpt-6-luna`
   with low reasoning is the tiny fixture's default. SDK 0.163.0 signatures were
   checked for `output_schema`, `effort`, thread start and resume. No higher-model
   routing, repair loop, or paid API-key fallback is introduced.
6. **Owner-controlled acceptance.** Tests live outside the executor workspace,
   with a pinned expected count and hashes. Source hashes detect later drift.
   The verifier subprocess remains an incomplete malicious-code boundary.
7. **Retain failed evidence.** The first live command blocked before any model
   turn. CLI `-c` paths require bare normal MCP identifiers; quoting them created
   an invalid separate entry. The corrected path was verified without inference;
   unusual names fail closed. Original blocked records/logs are preserved.
8. **Respect the run boundary.** The user prohibited automatically repeating a
   blocked live demonstration. Each subsequent attempt received explicit human
   authorization. The final cycle completed with exactly three real turns in
   total. Rotation/compaction and repair remain later phases.
9. **Retain SDK role handles through a cycle.** An explicitly authorized second
   attempt exposed that a fresh empty thread cannot be resumed from a different
   process. The first turn now follows creation in the same worker, with its
   SQLite session record committed first. The worker caches the distinct role
   handles for planning/execution/review and closes at the cycle boundary. A
   no-inference SDK roundtrip tested this correction before the subsequently
   authorized real cycle passed. Both blocked attempts were preserved. The final
   suite has 43 passing tests, including correct aggregation of failing subtests.

## Fase 3A: decisiones vigentes

1. Pello desarrolla automatización de negocio: la entrega final exige recursos
   reales verificados. Esta ampliación sigue local y no completa la V1.
2. Pipeline sobre la base existente, migración aditiva v3 y tablas históricas
   preservadas. Claves task/attempt/phase permiten intercambios repetidos sin
   eliminar los presupuestos configurables. supervised conserva su límite de tres.
3. El dueño fija contrato inicial y suites; la IA produce arquitectura/instrucciones
   y Python controla gates. Replanificar criterios no es parte de una reparación.
4. Tester determinista y Reviewer sobre supervisor read-only. Frecuencia configurable;
   riesgo alto siempre se revisa. Tests fallidos jamás se aprueban por opinión IA.
5. Dependencias requieren aprobación y checkpoint; se reejecutan suites anteriores.
   Git/SQLite se reconcilian con intención PREPARED, padre, mensaje y fuente.
6. Luna/Sol por riesgo/historial y capacidad observable, modelo enviado por turno;
   catálogo/esfuerzo validados y razón registrada. Sin Astra ni API de pago.
7. Configuración de herramientas por proyecto con referencias no secretas y
   límites explícitos. En Fase 3A solo Python/Git; n8n necesita un adaptador DEV.
8. La solicitud actual prioriza pipeline antes de rotación; el antiguo orden de
   fases queda histórico. Demo real: cinco turnos y un intento por incremento;
   reparaciones e interrupciones se prueban principalmente con respuestas inyectadas.
