# PELLO V1 — PHASE 3
## Product Alignment, Incremental Development Pipeline & Autonomous Execution

**Organization:** ATHIS GROUP  
**Product name:** PELLO  
**Execution model for this development session:** GPT-6.1 Sol, High reasoning  
**Existing installation:** `C:\Users\USUARIO\OneDrive\Documents\ChatGPT\DESARROLLO PELLO\Pello`  
**Current baseline:** Phase 2, commit `61f52e7`, branch `codex/pello-phase2`, subject to verification against the actual repository.

## 1. Critical clarification: What Pello actually is

Pello is NOT merely an autonomous code generator.

Pello is ATHIS GROUP's internal autonomous software development and business automation engineer.

Its purpose is to transform client product specifications into implemented, integrated, tested, and documented solutions with minimal ongoing human supervision.

The intended user workflow is:

1. The founder agrees on the product scope with a client.
2. The founder provisions the necessary infrastructure, such as Railway instances, n8n, databases, and credentials.
3. The founder identifies which external systems Pello may access.
4. The founder supplies a product specification, constraints, and acceptance criteria.
5. Pello analyzes the project and produces an implementation plan.
6. Pello independently develops the solution using Codex, MCP, APIs, browser/computer interaction when supported, and authorized connected tools.
7. Pello tests each increment, diagnoses errors, fixes them, and continues.
8. Pello maintains accurate project memory and resumes across model sessions and process interruptions.
9. Pello works unattended while the host computer, connectivity, authentication, permissions, and service quotas allow it.
10. Pello sends daily progress reports by email.
11. Pello delivers an implemented and verified system, relevant deployment artifacts, documentation, and outstanding issues for final review.

**Pello must eventually complete real business automation projects, not merely produce files that appear correct.**

A delivered n8n solution must exist in the authorized instance and have verifiable execution evidence.

Generating a workflow JSON without deploying or testing it in the approved development environment is insufficient.

The founder is responsible for business scope, infrastructure provisioning, credential authorization, and final approval—not continuous technical supervision.

This is the acceptance target of Pello V1.

The current implementation is only a foundation.

## 2. Current verified foundation

Phase 2 already demonstrated:

- A real AI supervisor.
- A separate Codex executor.
- Automated Python message transfer.
- Structured messages.
- SQLite persistence.
- Independent Python verification.
- A real supervised development task.
- Three actual SDK turns.
- Twelve passing acceptance tests for the generated implementation.
- Forty-three passing local tests.
- Persisted session identifiers.
- Reopening a completed project without repeated inference.

Do not recreate these components.

Inspect the actual repository and evidence before modifying anything.

Relevant modules include:

- `ai_supervisor.py`
- `supervised.py`
- `bridge.py`
- `messages.py`
- `codex_worker.py`
- `verification_worker.py`
- `cli.py`

Read the existing product state, decisions, and test reports.

The current Phase 2 workflow handles one bounded development task.

It does not yet support complete business-project execution.

## 3. Mandatory development philosophy

We are introducing an incremental development methodology.

The key principle is:

**Smaller functional increments → narrower tests → earlier failure detection → more localized corrections → less accumulated rework.**

This is a working hypothesis to implement and measure, not a guarantee that smaller tasks are always faster.

Avoid both extremes:

- One enormous implementation prompt covering an entire product.
- Hundreds of trivial microtasks that create excessive coordination overhead.

Instead, the planner must produce cohesive, independently verifiable functional increments.

Each increment should:

- Deliver a meaningful behavior.
- Have explicitly defined inputs and outputs.
- Identify dependencies.
- Have measurable acceptance criteria.
- Affect a bounded set of components.
- Be independently testable.
- Leave the repository or integration in a consistent state.

The system should verify each increment before starting dependent work.

Do not accumulate numerous unverified changes.

## 4. The proposed development pipeline

The conceptual structure is:

PRODUCT SPECIFICATION
↓
GLOBAL PLANNER
↓
INCREMENTAL TASK QUEUE
↓
CODER
↓
TESTER
↓
REVIEWER
↓
PASS → CHECKPOINT → NEXT INCREMENT
OR
FAIL → DIAGNOSE → CORRECT / REPLAN / ESCALATE

Repeat until the product meets its acceptance criteria or encounters a legitimate blocker.

### Important: These are responsibilities, not four permanently running agents

Do not create four long-lived processes merely to reproduce a video.

Pello Core coordinates the pipeline.

The same model may perform different responsibilities when appropriate.

Different models and reasoning levels may be selected dynamically.

The architecture should allow specialist review without requiring expensive AI calls after every trivial edit.

The main objective is reliable incremental execution.

### Planner

Responsibilities:

- Read the entire product specification.
- Inspect the actual project state.
- Design the necessary architecture.
- Identify external services and tools.
- Define interfaces, dependencies, and failure cases.
- Establish acceptance criteria.
- Divide work into functional increments.
- Define their verification strategy.
- Replan only when new evidence requires it.

The global plan must remain available to every subsequent increment.

The planner should not redesign the entire product after every small code change.

### Coder

Responsibilities:

- Receive one bounded increment.
- Read its specification and relevant context.
- Implement only the requested scope.
- Use authorized tools and APIs.
- Perform routine local checks.
- Record actual changes and external resource identifiers.
- Return evidence and unresolved issues.

The Coder must not silently expand scope or alter protected acceptance criteria.

### Tester

Responsibilities:

- Verify expected behavior.
- Run existing deterministic tests.
- Cover expected and negative scenarios.
- Detect regressions.
- Identify missing evidence.
- Return specific reproducible failures.

Where AI-assisted test design is valuable, the Tester should derive additional tests from the product specification, preferably before examining the implementation.

Routine test execution should remain deterministic whenever possible.

A failure should be returned with precise reproduction information, not simply "the implementation is wrong."

### Reviewer

Responsibilities:

- Inspect the increment specification.
- Inspect the implementation and Git diff.
- Read the actual test evidence.
- Check compatibility with the global architecture.
- Detect omissions, regressions, unsafe shortcuts, and specification mismatches.
- Return PASS, FAIL, or BLOCKED.

The Reviewer must be technically read-only with respect to implementation code and protected acceptance tests.

A PASS cannot override objective test failures.

The Reviewer should operate at meaningful functional boundaries and earlier for high-risk changes.

Its frequency is a policy to evaluate, not a fixed mandatory model call after every minor operation.

### Feedback and escalation

When a test or review fails:

1. Identify the specific failed requirement.
2. Diagnose whether the problem is implementation, specification, integration, or infrastructure.
3. Return actionable feedback to the appropriate responsibility.
4. Attempt a bounded correction.
5. Re-run relevant tests.
6. Preserve previous successful evidence.
7. Escalate reasoning or model capability when justified.

Escalation should consider:

- Repeated failure without measurable progress.
- Architectural contradictions.
- Persistent misunderstanding of requirements.
- Risk and complexity.
- Context degradation.
- Historical attempts and diagnostics.

Do not hard-code three or four attempts merely because those numbers appeared in an example.

Use configurable limits and evidence-based decisions.

Do not restart an entire project to fix one failed increment.

## 5. Dynamic model selection

Model selection is subordinate to the development pipeline.

Pello should dynamically choose an available model and reasoning effort based on task complexity, risk, past failures, and remaining usage capacity.

Initial experimental preference:

- Economical Luna configurations for routine implementation.
- Sol for more demanding planning, integration, debugging, and review.
- Escalation when lower-cost reasoning is insufficient.

The operational aspiration is to complete roughly 70–80% of appropriate execution work using economical model configurations, if benchmark results justify it.

This is NOT an enforced percentage.

Never sacrifice correctness just to reach a model-usage target.

**Do not use Astra inside the Codex pipeline.**

Do not automatically introduce paid API billing or Claude integrations.

Use existing authenticated ChatGPT/Codex access where compatible.

Validate actual model IDs and reasoning levels against the installed environment.

Record model choice, effort, results, and available usage metadata for later evaluation.

### External ChatGPT Reviewer

Preserve architectural extensibility for a future optional ChatGPT reviewer that exchanges evidence and decisions with Pello through a supported connector or MCP interface.

Do not assume normal ChatGPT conversations provide an unrestricted programmatic inference API.

Do not make this integration a dependency of the autonomous pipeline.

Do not implement it in this phase.

## 6. Pello Core and tool integration

Pello must be capable of performing work, not merely reasoning about it.

The eventual V1 must support authorized access to relevant external tools, including:

- Codex for coding and technical operations.
- n8n through compatible MCP capabilities or documented APIs.
- Railway-hosted resources where appropriately authorized.
- Databases and service APIs.
- Google services through supported connectors/APIs.
- Browser or computer interaction when supported and permitted.
- Other tools explicitly provisioned for a client project.

Not every tool must be available for every project.

Implement a project-specific tool configuration approach.

Each project should identify:

- Available tools.
- Connection identifiers or non-secret credential references.
- Allowed operations.
- Environment: local, development, staging, or production.
- Relevant resource identifiers.
- Permission boundaries.
- Expected verification methods.

Do not store raw credentials in Markdown, SQLite logs, or Git.

Use existing secure authentication and configuration mechanisms where possible.

The Phase 2 SDK worker intentionally disabled inherited MCP servers, apps, and other integrations for isolation.

That configuration must not be treated as Pello's final operational tool policy.

The eventual executor must support explicitly authorized tools without exposing unrelated credentials or granting unrestricted global access.

Inspect version-specific capabilities rather than assuming all Codex, MCP, plugin, or Computer Use features are available.

## 7. Durable context and project continuity

The system must never lose track of what it is building.

Maintain three layers:

### Product memory

- Business goal.
- Scope.
- Constraints.
- Architecture.
- Acceptance criteria.
- Approved integrations.
- Important decisions.

### Execution memory

- Functional increments.
- Dependencies.
- Current status.
- Attempts.
- Changes.
- Tests.
- Tool operations.
- External resource identifiers.
- Failures.
- Model sessions.
- Checkpoints.

### Active agent context

Construct a bounded context for each increment using:

- Global project objective.
- Current increment.
- Applicable constraints.
- Relevant files and interfaces.
- Prior verified dependencies.
- Unresolved errors.
- Required acceptance tests.
- Latest confirmed external system state.

Do not resend complete conversation histories.

Persist essential decisions and evidence before session replacement or interruption.

The future system must support configurable rotation and recovery for all relevant roles.

A new session should be able to reconstruct the work state without repeating completed operations.

External operations require reconciliation before retrying when their completion status is ambiguous.

## 8. Daily operation and reporting

Pello V1 must eventually run unattended on the founder's local Windows computer.

The computer must remain powered on, awake, connected, and authenticated.

Do not design an unnecessary cloud-hosted Pello infrastructure for V1.

Required eventual operational features:

- Autonomous task continuation.
- Persistent execution state.
- Safe pause and resume.
- Quota-aware interruption handling.
- Recovery after crashes or restarts.
- Configurable retry/escalation policies.
- Scheduled progress reporting.
- Daily email delivery.
- Final delivery report.

Reports must show meaningful verified progress, not invented AI percentages.

Separate:

- Implementation progress.
- Acceptance criteria satisfied.
- Integration verification.
- Blockers.
- Remaining work.

The user should be able to receive a report such as:

PELLO — DAILY STATUS

Project: Client Automation
Status: IN PROGRESS
Verified functional increments: 7/11
Acceptance criteria: 16/21
Current activity: Integration verification
Blocked dependencies: None
Next action: Complete the current verified increment
Usage: Recorded model turns and measurable consumption

These figures are examples, not required values.

Implement report generation using persisted evidence.

Email delivery should eventually use an explicitly authorized mailbox and must be testable without sending real messages.

Do not claim 24/7 uninterrupted operation or unlimited Codex usage.

When quota is exhausted, preserve state and pause safely.

## 9. Final Pello V1 acceptance target

The complete V1 must eventually demonstrate the following workflow:

1. The founder provides a realistic business automation product sheet.
2. Authorized development infrastructure and credentials are supplied separately.
3. Pello understands the project and creates a global plan.
4. The plan is divided into coherent verifiable increments.
5. Pello executes the increments through its pipeline.
6. It creates or modifies actual resources in an authorized development environment, including n8n where required.
7. It verifies actual external integration behavior.
8. It corrects detected failures autonomously within safe limits.
9. It escalates difficult problems appropriately.
10. It preserves context across sessions and interruptions.
11. It continues working without requiring prompt-by-prompt human coordination.
12. It generates and emails daily progress reports.
13. It delivers the implemented solution with test evidence, configuration references, documentation, and outstanding blockers.
14. Production activation or sensitive irreversible actions require explicit authorization.

Do not use the previous dental-booking demonstration as the default project or product target.

That example is illustrative only.

The acceptance target is the general ability to deliver business automation solutions from different product specifications.

---

# 10. Current implementation assignment

**This execution is Phase 3A: Product-aligned incremental pipeline foundation.**

DO NOT attempt the full V1 in one run.

Your task is to adapt the existing Phase 2 foundation toward the operational methodology described above.

### Step A — Audit the actual Phase 2 architecture

Inspect the current modules, SQLite schema, CLI, model configuration, and verified evidence.

Identify where the current one-task/three-turn limits are enforced.

Record the minimum required changes to support repeatable incremental execution.

Preserve existing data and backward compatibility.

### Step B — Update the product contract

Update `SPEC.md`, `PLAN.md`, `STATE.md`, and `DECISIONS.md` where appropriate.

Clarify that Pello's primary purpose is autonomous end-to-end business automation development, not simply source-code generation.

Use **Pello** consistently in user-facing interfaces, commands, reports, and documentation.

Historical internal module names such as `athis_autopilot` may remain temporarily to avoid unnecessary breakage.

Do not perform a risky mass rename.

### Step C — Extend the persistent execution model

Implement minimal additive changes that support:

- Multiple functional increments per project.
- Multiple attempts per increment.
- Repeated pipeline exchanges.
- Correlation between tasks, attempts, tests, and reviews.
- Status and dependency tracking.
- Separate role/session references.
- Evidence references.
- Git checkpoints.
- Durable progress across process restarts.

Avoid an unnecessarily elaborate generalized multiagent framework.

Do not destroy Phase 2 records or previous evidence.

### Step D — Implement the incremental pipeline

Extend the existing supervisor to support:

GLOBAL PLAN
→ SELECT NEXT READY INCREMENT
→ IMPLEMENT
→ VERIFY
→ REVIEW WHEN REQUIRED
→ CHECKPOINT
→ NEXT INCREMENT

On failure:

FAILURE
→ DIAGNOSE
→ REPAIR OR REPLAN
→ REVERIFY

For this phase, implement only the minimal orchestration needed to demonstrate consecutive functional increments.

Use the existing AI supervisor and Codex executor.

Add logical Tester and Reviewer responsibilities while reusing the current independent verifier.

The Reviewer must be read-only if instantiated as an AI session.

Do not introduce four mandatory model calls per increment.

Use objective test gates to control advancement.

Ensure a previously approved increment is not re-executed without a justified dependency change or explicit invalidation.

### Step E — Implement a bounded demonstration

Create a small, deterministic demonstration project requiring **two dependent functional increments**.

Each increment must:

- Have its own specification.
- Produce real changes.
- Have independent acceptance criteria.
- Execute local verification.
- Preserve state and evidence.
- Allow the next increment only after successful verification.

Demonstrate that the second increment uses the artifact from the first.

The demonstration must show actual Python-to-Codex automated coordination, not a predetermined fake success.

Use isolated, fictional data.

If a safe n8n development instance has already been explicitly configured, you may inspect available tool capabilities and document the viable integration path, but do not modify external workflows in this phase.

If no n8n connection exists, do not block the local pipeline demonstration.

Do not claim n8n capability has been verified by a Python-only test.

### Step F — Test reliability

Add deterministic tests for:

- Multi-increment planning.
- Task dependency enforcement.
- State transitions.
- Repeated exchanges.
- Attempt histories.
- Verifier rejection.
- Failed increment blocking its dependents.
- Reviewer read-only enforcement where supported.
- Checkpoint consistency.
- State restoration.
- No duplicate completion after resume.
- Compatibility with existing Phase 2 projects.

Run the existing test suites and correct regressions.

Use injected responses for most orchestration tests.

Run a small real SDK demonstration only after deterministic tests are passing.

Limit expensive live SDK usage. Do not automatically retry failed live demonstrations or trigger a large unattended run.

If the new multi-increment path cannot be verified live within the available usage constraints, identify it explicitly as unverified.

### Step G — Prepare the next implementation milestones

Produce a concrete roadmap toward completing Pello V1.

Prioritize the dependencies required to achieve:

1. Real incremental pipeline execution.
2. n8n MCP/API development integration.
3. Authorized external tool configuration.
4. Real integration tests and automated repair.
5. Context reconstruction and session rotation.
6. Reliable unattended continuation and recovery.
7. Scheduled daily email reports.
8. End-to-end acceptance testing using a real development automation project.

These items may overlap or be reordered when supported by actual technical dependencies.

The final roadmap must be based on the actual repository and remaining capabilities, not generic estimates.

---

# 11. Resource efficiency

We are operating within the limits of ChatGPT Plus and Codex.

Optimize verified progress per unit of available usage.

- Prefer short, verifiable implementation increments.
- Minimize unnecessary whole-repository reads.
- Avoid excessive context duplication.
- Reuse existing functions and data structures.
- Use deterministic tools instead of AI whenever sufficient.
- Do not invoke expensive models merely for simple checks.
- Do not exceed configured call, retry, or execution budgets.
- Do not introduce paid API usage automatically.
- Never fabricate passing tests or successful external integrations.
- Preserve state before stopping due to limits.

Model choice must remain adaptive.

The current development session uses Sol High because it involves architecture and persistence migrations. This does not mean Pello's nested agents should all use Sol High.

## 12. Scope boundaries

In this execution, DO NOT:

- Rewrite Pello from scratch.
- Deploy Pello to the cloud.
- Build a graphical dashboard.
- Modify client production systems.
- Create full HMP or Grupo ADSA products.
- Send real client messages.
- Implement uncontrolled parallel agents.
- Build a generic agent marketplace.
- Implement a paid API integration as a workaround.
- Spend the entire usage allowance on elaborate architecture documents.
- Automatically continue beyond Phase 3A.

**Deliver working, tested incremental pipeline functionality before adding advanced features.**

## 13. Final deliverables

At the end of this run:

1. Updated Pello V1 product definition.
2. Extended persistent task/attempt/exchange architecture.
3. Working incremental pipeline prototype.
4. Two dependent functional increments demonstrated, if permitted by authentication and quota.
5. Independent verification evidence.
6. Preserved Phase 2 behavior and regression tests.
7. Current state and checkpoint.
8. Remaining constraints.
9. Realistic next engineering milestone toward business automation delivery.
10. Concise report of actual model usage and verification results.

Respond in Spanish.

Clearly distinguish:

- IMPLEMENTED
- TESTED WITH MOCKS
- VERIFIED LOCALLY
- VERIFIED THROUGH REAL CODEX SDK
- VERIFIED IN REAL EXTERNAL INTEGRATION
- BLOCKED
- NOT IMPLEMENTED

Do not claim the complete Pello V1 is operational.

**Pello succeeds when it can independently deliver functional business automation systems, not when it merely simulates a development team.**

Start by inspecting the current Phase 2 repository and preserve everything already verified.

Execute Phase 3A, test it, save the project state, report results, and stop.