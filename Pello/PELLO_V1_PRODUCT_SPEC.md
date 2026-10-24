
# PELLO V1
## Product Specification — Internal Development Document

**Version:** 1.3  
**Reference date:** October 24, 2026  
**Type:** Functional definition, target architecture, scope, and requirements for Pello V1.  
**Purpose:** Define what Pello must do, how it must operate, which tools it needs, and which conditions must be met for Version 1 to be considered complete.

**This document defines the target behavior of Pello V1. It does not represent the current implementation status or imply that all features have already been developed.**

---

# 1. Definition of Pello

**Pello is an autonomous software development and automation system that transforms a product specification into an implemented, integrated, tested, and documented solution.**

I prepare the infrastructure, configure credentials, provide the necessary access, and define the scope through a product specification.

Pello handles the technical development work.

It must understand requirements, plan, break down work, select appropriate tools, develop, test, review, correct errors, preserve context, and continue working until the product is complete.

The goal is for me to provide a product specification, leave Pello working for hours, and receive a functional solution without personally directing every step.

## 1.1. Why Pello Exists

My current development workflow relies on manually coordinating ChatGPT and Codex:

1. I provide a product specification.
2. ChatGPT interprets the requirements and prepares a plan.
3. ChatGPT generates instructions for Codex.
4. Codex develops and executes tests.
5. I copy Codex's results back into ChatGPT.
6. ChatGPT analyzes the results and generates the next instructions.
7. I repeat this process until the project is complete.

This method works, but it requires my constant involvement to transfer information, maintain context, select models, identify the next step, and continue after errors.

**Pello automates this entire cycle.**

It is not intended to replace the tools I already use. Instead, it coordinates them so they can work together autonomously.

## 1.2. Expected Outcome

The ideal Pello V1 workflow is:

**PRODUCT SPECIFICATION → PLANNING → INCREMENTAL DEVELOPMENT → TESTING → REVIEW → CORRECTION → INTEGRATION → FUNCTIONAL DELIVERY**

Throughout the process, Pello maintains memory, manages its work, uses real tools, and sends progress reports.

---

# 2. Responsibilities and Project Preparation

## 2.1. What I Prepare

### Product Specification

I provide a document containing, as applicable:

- Product objective.
- Problem being solved.
- Requested features.
- Business rules.
- Required integrations.
- Expected behavior.
- Constraints and exclusions.
- Special conditions.
- Expected outcomes.

The specification may be written in natural language.

**I should not have to manually transform every requirement into technical tasks, acceptance tests, or agent prompts.**

### Infrastructure

I prepare the required resources:

- One primary n8n instance hosted on Railway.
- Credentials configured within n8n.
- Required databases.
- Repositories when applicable.
- Access to external services.
- Project-specific configuration and resources.

**Pello V1 operates on a single n8n instance hosted on Railway, which may be a production instance.**

There is no requirement to create a separate development instance or maintain two copies of the same workflow to move from testing to production.

The instance may contain previously delivered workflows, workflows under development, and newly created workflows.

### MCP Connection

I manually configure the connection between Codex and the official n8n MCP server using the corresponding `config.toml` file.

I am also responsible for authenticating the connection and enabling MCP access to the workflows Pello is supposed to develop or maintain.

Pello reuses this existing connection.

**Pello does not need to build its own MCP server or an n8n proxy for V1.**

The initial configuration must be verified before Pello begins performing operations.

### Permissions and Limits

I define:

- Which workflows Pello may work on.
- Available connections and credentials.
- Required external services.
- Authorized operation types.
- Permitted external effects.
- Time and usage limits.
- Actions requiring additional approval.

Initial authorization may cover multiple subsequent operations.

**Pello must be able to work without requesting permission for every increment, as long as it remains within the authorized scope.**

## 2.2. What Pello Does

Pello must:

1. Read and interpret the product specification.
2. Identify contradictions, ambiguities, and incomplete requirements.
3. Design the technical solution.
4. Break the work into functional increments.
5. Define contracts and acceptance criteria.
6. Design and execute tests.
7. Write code and use external tools.
8. Create and modify real workflows.
9. Publish and test workflows when appropriate.
10. Correct errors autonomously.
11. Review the quality of changes.
12. Maintain memory and checkpoints.
13. Continue after recoverable interruptions.
14. Manage model selection, reasoning effort, and limits.
15. Send daily reports.
16. Deliver the completed product with evidence.

**Pello must make normal technical development decisions without constantly consulting me.**

It should request intervention only when essential information is missing, authorization is required, or a blocker cannot be resolved safely.

---

# 3. Incremental Development Methodology

Pello's fundamental principle is to develop through small, functional, verifiable, and frequent increments.

The objective is not to build one enormous solution and test everything only at the end.

Instead, the goal is to reduce the number of changes that could be responsible for a failure.

### Core Relationship

**Small increments → frequent, focused tests → easier error localization → faster corrections.**

This does not mean every task must be microscopic.

The objective is to find an appropriate size: small enough to preserve context and detect failures early, but large enough to produce verifiable functionality.

## 3.1. DORA Foundation

Research from DORA (DevOps Research and Assessment) supports working in small batches, integrating frequently, automating tests, and maintaining rapid feedback loops.

These practices are associated with stronger software delivery capabilities and help detect problems before accumulating changes that are difficult to verify.

DORA also identifies that accelerated AI-assisted code generation can increase instability when it is not accompanied by sound integration practices, testing, and small changes.

Pello adopts these principles as the foundation of its development methodology.

**The implementation of Planner, Coder, Tester, and Reviewer is a Pello architectural decision, not a specific DORA requirement.**

Source: https://dora.dev/capabilities/working-in-small-batches/

## 3.2. Development Pipeline

The logical pipeline is:

**PRODUCT SPECIFICATION → GLOBAL PLAN → INCREMENT → CONTRACT → PROTECTED TESTS → CODER → TESTER → REVIEWER → CHECKPOINT → NEXT INCREMENT**

When a failure occurs:

**FAIL → DIAGNOSIS → CODER OR PLANNER → CORRECTION → REVERIFICATION**

This cycle repeats until the product is complete.

Planner, Coder, Tester, and Reviewer are **logical responsibilities**.

There is no requirement to maintain four permanently running AI processes or use four different models for every increment.

Pello Core coordinates when each responsibility should be invoked.

## 3.3. Planner

The Planner is responsible for understanding and organizing development.

It must:

- Interpret the entire product.
- Design the architecture.
- Identify required tools.
- Divide the product into increments.
- Establish dependencies.
- Define objectives and acceptance criteria.
- Prepare technical contracts.
- Prepare precise instructions for the Coder.
- Adapt each increment's difficulty to the capabilities of the executing model.
- Reorganize the technical plan when evidence justifies doing so.

**The Planner must plan according to the Coder's capabilities.**

For example, if the Coder uses Luna and a feature is too large, the Planner must divide it into more manageable tasks.

The Planner does not need to reconstruct the entire plan after every approved increment.

## 3.4. Contract for Each Increment

Before tests are prepared, the Planner defines the behavior the Coder must implement.

The contract includes, when applicable:

- Functional objective.
- Related requirements.
- Inputs.
- Expected outputs.
- Interfaces.
- Webhook routes.
- Payload structures.
- Business rules.
- Dependencies.
- Expected external effects.
- Acceptance criteria.

The contract must describe **what needs to work**, without imposing unnecessary implementation details.

Tests are designed against this contract.

If the contract is ambiguous, it must be corrected before proceeding.

Not every increment requires an HTTP contract or a complex schema. The structure must be appropriate for the type of functionality.

## 3.5. Coder

The Coder receives a specific increment and is responsible for implementing it.

It must:

- Work only within the assigned scope.
- Consult relevant files, resources, and tools.
- Implement real code or configurations.
- Create or modify authorized workflows.
- Execute local checks.
- Record changes and operations.
- Report errors or missing dependencies.

The Coder cannot modify acceptance criteria to obtain an artificial PASS.

If an increment is too complex, the Coder may receive smaller instructions or be escalated to a more capable model.

## 3.6. Tester

The Tester has two responsibilities.

### Before Implementation

- Interpret the contract.
- Design happy-path tests.
- Design tests for failures and edge cases.
- Prepare independent verification.
- Record the tests that must pass.

### After Implementation

- Execute the tests.
- Compare observed results with expected results.
- Detect failures and regressions.
- Return reproducible diagnoses.
- Verify that a correction resolves the original problem.

Routine tests should be executed using deterministic tools whenever possible.

There is no need to spend an AI inference call checking every simple result.

## 3.7. Test Protection

Before an increment is delivered to the Coder:

1. The Planner establishes its contract and acceptance criteria.
2. The Tester prepares the tests.
3. Pello Core records those tests.
4. Their hashes are calculated and stored.
5. The acceptance test set is protected.
6. The Coder receives the increment.

Acceptance tests must remain outside the Coder's write permissions.

If the Coder modifies, deletes, or weakens protected acceptance test files, Pello invalidates the attempt.

If a test contains a legitimate error, the Tester may correct it through a controlled procedure, with justification and a new hash.

Additional tests may also be added when relevant cases arise that were not originally considered.

The Coder may know the expected behaviors, but it cannot alter the definition of success.

## 3.8. Reviewer

The Reviewer evaluates whether an increment actually meets its requirements.

It must review:

- Applicable requirements.
- Technical contract.
- Modified code and configurations.
- Git diff.
- Test results.
- External integration evidence.
- Compatibility with previous increments.
- Potential regressions.

**The Reviewer uses an independent evaluation session.**

It must not inherit the Planner's private reasoning or the Coder's explanations as if they were verified facts.

It may consult the objective context required to understand the product and its dependencies.

It has read-only access to code and protected tests.

Its role is to issue an evidence-based verdict, not directly correct the implementation.

A Reviewer PASS can never override a FAIL from mandatory tests.

## 3.9. Correction and Escalation

When a failure occurs, Pello must identify its nature.

### Implementation Error

The Coder receives the diagnosis, corrects the increment, and runs the relevant tests again.

### Design Error

The Planner analyzes the problem and adjusts the technical plan or task decomposition.

### Integration Error

Pello checks the external tool's state, identifies the affected resource, and determines how to correct the problem.

### Persistent Error

If multiple attempts fail to produce sufficient progress, Pello may:

- Change the technical approach.
- Break down the increment further.
- Request a deeper review.
- Increase reasoning effort.
- Escalate the Coder from Luna to Sol.
- Stop the increment when authorized limits are reached.

There is no universal number of attempts that applies to every problem.

Pello evaluates the error type, progress achieved, risk, and available resources.

Corrections should remain localized to the affected functionality whenever possible.

Pello must not restart an entire product to repair a small problem.

---

# 4. Adaptive Model Policy

Pello uses different model configurations depending on the responsibility, complexity, and observed behavior.

Model selection is not the system's main purpose.

It is a tool for achieving high-quality and efficient development.

## 4.1. Default Configurations

| Responsibility | Default Configuration | Adaptation |
| --- | --- | --- |
| Planner | Sol High | May downgrade to Luna for simple planning. |
| Coder | Luna Medium | May escalate to Sol for difficult work or persistent failures. |
| Tester | Variable | Python for routine tests; AI when test design or analysis is needed. |
| Reviewer | Sol High | May adjust reasoning effort according to risk while preserving independence. |

The Tester's default configuration depends on the type of work.

Sol Medium is an option for tests requiring reasoning, not a permanent requirement.

## 4.2. The 70–80% Guideline

The intention is for Pello to use its usual role-specific configurations in approximately **70–80% of the relevant invocations**, when task characteristics allow it.

This does not mean using inexpensive models for 70–80% of execution time.

It is also not a rigid quota.

The objective is for Pello to normally use:

- Sol for planning.
- Luna for coding.
- A variable configuration for testing.
- Sol for reviewing.

And to adapt when appropriate.

Examples:

- Trivial planning may use Luna.
- Difficult implementation work may use Sol from the beginning.
- A Coder repeatedly encountering errors may temporarily escalate to Sol.
- A high-risk review may require deeper analysis.
- Deterministic tests do not require additional AI inference.

After resolving a difficult problem, Pello may return to its usual configuration.

## 4.3. Limits

- Pello may select models and reasoning effort per invocation.
- It must validate actual availability before selecting a model.
- It must not silently substitute unavailable models.
- It must record the configuration used and its results.
- It must respect Codex usage limits.
- Astra is excluded from the V1 Codex pipeline.
- A paid API is not required to operate the initial core.

The names Sol and Luna represent model profiles. Their technical identifiers must be resolved against the actually available model catalog.

A possible future integration of ChatGPT Chat as an external Reviewer is not a mandatory V1 requirement.

---

# 5. Pello V1 Architecture

## 5.1. Pello Core

Pello Core is the main controller, implemented in Python.

Its responsibilities include:

- Receiving the product specification.
- Managing projects.
- Coordinating logical agents.
- Selecting ready increments.
- Managing dependencies.
- Choosing models and reasoning effort.
- Enabling authorized tools.
- Controlling tests and reviews.
- Managing attempts and corrections.
- Enforcing execution limits.
- Persisting memory.
- Recovering work.
- Generating reports.
- Determining whether the product is complete.

Process states must be managed in a structured way.

An AI-generated statement is not a substitute for objective verification.

## 5.2. Persistence

Pello uses:

### SQLite

To store projects, tasks, requirements, dependencies, attempts, sessions, decisions, tests, results, external operations, and reports.

### Git

To preserve code, exportable configurations, diffs, checkpoints, and recoverable versions.

### Markdown Files and Structured Documents

To preserve product specifications, the global plan, technical decisions, architecture, and durable context.

## 5.3. Memory and Context Reconstruction

Pello does not need to remember every complete conversation.

It needs to accurately reconstruct the project's state.

Three layers are distinguished:

### Product Memory

- Objective.
- Requirements.
- Scope.
- Architecture.
- Decisions.
- Integrations.
- Acceptance criteria.

### Execution Memory

- Increments.
- Attempts.
- Errors.
- Changes.
- Tests.
- Checkpoints.
- External resources.
- Pending operations.

### Active Context

Information relevant to the next invocation:

- Overall objective.
- Current increment.
- Dependencies.
- Constraints.
- Required files and resources.
- Latest results.
- Pending errors.

Pello must be able to change sessions without losing approved work.

## 5.4. Session Rotation

Sessions may be replaced due to context limits, configuration, or continuity problems.

A new session must receive the reconstructed project state.

It must not repeat an already completed operation simply because it does not know the previous conversation.

If an external operation has an uncertain outcome, its actual result must be checked before attempting it again.

---

# 6. Initial Product Specification Validation

Before development begins, Pello runs a validation phase.

It must identify:

- Clear requirements.
- Ambiguous requirements.
- Contradictions.
- Missing dependencies.
- Technical assumptions.
- Unavailable resources.
- Actions requiring authorization.

Uncertainties are classified as:

**Blocking:** They prevent safe progress or may alter scope, produce significant effects, or affect sensitive information.

**Non-blocking:** They can be resolved through reasonable technical decisions without changing approved requirements.

Pello records non-blocking assumptions and continues.

If a blocking uncertainty exists, Pello requests clarification but may continue working on independent increments that do not depend on the answer.

Relevant assumptions must appear in progress reports.

---

# 7. Tools and Integrations

Pello must use real tools to implement products.

## 7.1. Main Tools

| Tool | Expected Use |
| --- | --- |
| Codex SDK | Development, code editing, and technical tasks. |
| Official n8n MCP | Creating, modifying, publishing, and testing workflows. |
| Railway | Prepared infrastructure for running n8n and required services. |
| External APIs | Integration with authorized business services. |
| Databases | Persistence and queries required by each product. |
| Git | Version control and recovery. |
| SQLite | Pello's internal state. |
| Computer Use / Browser | Operations through interfaces when compatible, authorized support exists. |
| Plugins and Connectors | Access to Drive, email, calendars, CRMs, and other compatible tools. |
| Email | Delivery of daily progress reports and final summaries. |

Different projects may require different tools.

Pello must discover which tools are available and select the appropriate ones.

It must never claim that an integration works unless it has performed and verified real operations.

## 7.2. Per-Project Configuration

Each project records:

- Available tools.
- Authorized resources.
- Workflow IDs.
- Credential references.
- Permitted operations.
- Constraints.
- Verification methods.

Credentials are used through secure mechanisms and references.

Secret values must not be copied into Markdown, logs, prompts, or evidence.

## 7.3. n8n Through the Official MCP Server

The primary connection between Pello and n8n uses the instance's official MCP server.

The connection is configured manually through `config.toml`, using a compatible authentication mechanism.

Pello reuses that connection.

**Pello must not build its own proxy, another n8n server, or an additional infrastructure layer for normal operations.**

The installed n8n version must provide the tools necessary to create, modify, publish, and test workflows.

If a required capability is unavailable through MCP, Pello must identify the limitation and record the blocker or request authorization for a specific alternative.

It must not assume that every access method provides the same permissions.

---

# 8. n8n: Single Instance, MCP Access, and Real Publishing

This section defines Pello's expected interaction with n8n.

## 8.1. One Instance

Pello V1 uses one primary n8n instance hosted on Railway.

That instance may be published and used by live systems.

**There is no requirement to maintain a separate DEV instance or a duplicated workflow to move from development to production.**

Pello works directly on the corresponding workflow and preserves its versions.

When a solution requires multiple workflows for functional reasons, Pello may create them.

What must be avoided is duplicating workflows solely to simulate separate environments.

## 8.2. Workflow Selection Through MCP

Operational access to workflows is primarily controlled through n8n's native **Available in MCP** setting.

The operating rule is:

**Workflow under development or maintenance → MCP access enabled.**

**Completed and delivered workflow → MCP access disabled.**

A delivered workflow may remain published, active, and serving users even when it is no longer available for modification or execution through MCP.

It must not be unpublished merely to remove Pello's access.

If future maintenance is required, I can re-enable its MCP access.

### Actual Scope of the Control

MCP availability restricts access to the complete contents and operations of workflows that are not MCP-enabled.

However, certain search tools may still display basic information about workflows visible to the authenticated user, even if those workflows are not enabled for MCP access.

Therefore, **disabling MCP must not be described as making a workflow completely invisible**.

Access also depends on the permissions of the authenticated user or connection.

MCP-enabled workflows may be available to other authorized MCP clients that have access to them. This setting must not be interpreted as a separate permission list for each client.

## 8.3. New Workflows

Pello may create new workflows through the official MCP server.

When it creates one:

1. n8n returns the workflow ID.
2. Pello records that ID in SQLite.
3. It associates the ID with the corresponding project.
4. It preserves the relevant state and configuration.
5. It verifies that it can continue working on the resource.
6. It records subsequent operations.

Official workflow creation tools may automatically mark a new workflow as available through MCP.

Pello must verify the actual result instead of assuming the resource's state.

I should not need to register every new workflow ID manually for Pello to continue developing.

Access to a newly created workflow does not automatically grant unlimited authorization to use credentials or generate external effects.

## 8.4. Freedom to Publish

Pello must be able to:

1. Create a workflow.
2. Configure it.
3. Connect authorized credentials.
4. Save its changes.
5. Publish it when necessary.
6. Execute tests through real endpoints.
7. Inspect executions and results.
8. Correct errors.
9. Publish a new version.
10. Keep the workflow operational after completion.

**Publishing a workflow does not require separate human approval every time if the initial authorized scope already covers that type of operation and its effects.**

This freedom is necessary because certain integrations, webhooks, and triggers require a published version to work correctly.

Publishing is part of the normal development process.

It must not automatically be treated as a prohibited operation merely because Pello is working on a production instance.

## 8.5. Draft and Published Versions

When the installed n8n version supports it, Pello uses its draft and published version mechanisms.

The expected workflow is:

**CURRENT WORKFLOW → EDITING → TESTING → REVIEW → PUBLISHING → REAL VERIFICATION**

There is no need to create a separate workflow solely to represent a draft.

If the workflow is already serving users, modifications should preserve its operation until the new version is ready, whenever n8n's capabilities support that separation.

Pello must determine which publishing mechanism the installed version supports.

It must not assume that saving equals publishing or that publishing guarantees every trigger is operational.

## 8.6. Testing Through Production Webhooks

Pello may use production webhook endpoints to perform integration tests.

This is especially important when an external integration requires a persistent public URL.

However, **using a production endpoint does not mean sending test data to real customers**.

Depending on the project, tests should use:

- Synthetic payloads.
- Test contacts.
- Phone numbers authorized for QA.
- Test accounts.
- Records identified as test data.
- Specifically authorized auxiliary resources.
- Verification of actual results.

When appropriate, Pello must use authentication, input filters, or other suitable barriers to prevent unintended effects.

It must not assume a webhook is safe merely because its payload contains a test label.

If there is no safe way to execute a test with external effects, Pello must record the blocker and continue with the verification activities it can safely perform.

### Records Created During Testing

Test resources created in external services must be identified and recorded.

Upon completion, Pello must:

- Delete them when safe and authorized.
- Or leave them clearly identified as test data.
- Report which ones remain and why.

It must not delete real production records by mistaking them for QA data.

## 8.7. Autonomous Publishing

Pello may autonomously publish or update workflows within the authorized scope.

Before publishing a change that could affect existing operations, it must:

1. Identify the workflow by its ID.
2. Verify that it is authorized and available through the relevant connection.
3. Preserve a recoverable version of its previous state when applicable.
4. Verify relevant requirements.
5. Review the changes.
6. Publish the authorized version.
7. Verify its actual publishing status and triggers.
8. Run post-publication tests when appropriate.
9. Record the result.

These operations are part of the normal pipeline and do not require my approval at every step.

Irreversible actions or actions exceeding previously authorized effects require additional intervention.

## 8.8. Versioning and Restoration

Pello preserves enough history to identify what changed.

For modified workflows, it must record:

- Workflow ID.
- Previous state and version.
- Previous exportable configuration when applicable.
- Changes made.
- New state and version.
- Publishing result.
- Verification executions.
- Subsequent errors.

Git is the primary mechanism for preserving exports and non-secret configurations.

Native n8n history and restoration mechanisms may also be used when available.

**Internal version control must not turn into a second deployment platform.**

Its purpose is to maintain traceability and enable recovery of previous configurations.

Restoring a workflow does not automatically reverse external effects that have already occurred.

For example, restoring a version does not retract a WhatsApp message that has already been sent.

Pello must distinguish between technical restoration and compensation for external effects.

## 8.9. Failures After Publishing

If a new version fails:

1. Pello detects the problem.
2. It determines whether the problem is related to the latest change.
3. It prevents additional dangerous operations.
4. It prioritizes restoring a previous version when a regression has been confirmed and restoration is safe.
5. It verifies that restoration worked.
6. It preserves the diagnosis.
7. It corrects the responsible increment.
8. It repeats verification before publishing again.

Not every failure requires an automatic rollback.

The decision depends on risk, system state, and whether restoration can be performed without causing additional harm.

## 8.10. Delivery and Removal of MCP Access

When Pello completes a product:

1. It verifies that the requirements are satisfied.
2. It confirms that the published workflow operates correctly.
3. It preserves evidence and references.
4. It generates the final report.
5. It identifies workflows whose development stage has ended.

Afterward, MCP access to those workflows should be removed through n8n.

**Managing MCP access is part of the instance configuration and may be performed manually by the user.**

Pello must identify which workflows are ready to have MCP access disabled, without requiring them to be unpublished.

A product may continue operating in production without Pello retaining permission to modify it.

---

# 9. Security and Action Controls

Pello must operate autonomously within an authorized scope.

Security must not depend solely on asking the model to be careful.

It must use effective tool permissions and apply controls over the operations it coordinates.

## 9.1. Security Through MCP

The primary restriction on access to existing workflows uses n8n's official MCP controls.

I enable the workflows Pello is allowed to work on.

Delivered workflows are no longer made available through MCP.

**Pello does not need to build a custom permission proxy for V1.**

However, this simplification requires verifying that:

- The MCP connection works correctly.
- The n8n version supports the required operations.
- Authorized workflows are MCP-enabled.
- Protected workflows cannot be edited or executed through that connection.
- Pello's executing process does not have an alternative route with equivalent privileges that could bypass those restrictions.

For example, the executor must not also receive an n8n administrative API key that would allow it to modify excluded workflows through direct HTTP requests.

MCP configuration does not automatically restrict every other tool, plugin, or access method that might be available to Codex.

## 9.2. Credentials

Required credentials are configured in n8n beforehand.

Pello must use them through compatible references without exposing secret values.

Some workflow creation tools may automatically assign accessible credentials.

Therefore, Pello must verify which credentials have been attached to nodes before publishing or executing operations with real-world effects.

Only credentials appropriate for the product and its authorized actions may be used.

**MCP access to a workflow does not replace checking the effects that its credentials can produce.**

Secrets must not be copied into Markdown, prompts, logs, or evidence.

## 9.3. External Effects

Three situations are distinguished.

**Reversible technical operations:** Code or configuration changes whose restoration can be reasonably controlled.

**Controlled external operations:** Tests using authorized recipients or resources, test records, and previously permitted publishing actions.

**High-impact operations:** Real bulk messaging, charges, deletion of important data, scope changes, or irreversible actions not covered by the initial authorization.

The first two categories may be performed automatically within their limits.

The third category requires explicit authorization or must be blocked.

## 9.4. Budgets and Circuit Breakers

Pello Core must enforce mandatory operational limits.

Their values are configurable.

They include:

- Maximum time per increment.
- Per-project budget.
- Maximum number of attempts.
- Escalation limit.
- External operation limit when applicable.
- Restrictions when progress stops.

If the SDK cannot directly enforce a monetary or token limit in real time, Pello must enforce measurable limits on turns, time, and operations, and record whatever usage data is available without claiming controls it cannot guarantee.

When a hard limit is reached:

- Pello stops the affected increment.
- It saves the current state.
- It records the reason.
- It does not automatically grant itself additional budget.
- It may continue with independent tasks that remain within authorized limits.
- It reports the blocker.

## 9.5. Emergency Stop

There must be a simple way to stop Pello from initiating new operations without depending on the agent being responsive.

**Stopping Pello does not mean automatically disabling workflows that are already operating.**

The emergency stop halts the orchestrator and prevents new actions from being initiated.

If a specific workflow needs to be disabled, that must be handled as a separate operation with a defined scope.

An external operation that has already started may continue even if the local process stops.

Pello must reconcile its state when resumed.

## 9.6. Code Isolation

Generated code may contain errors or dangerous behavior.

Pello must use permission limits and isolation proportional to the risk of the code it executes.

Automated testing and integrity controls do not, by themselves, replace operating-system isolation.

## 9.7. Objective Acceptance Rule

**No AI may turn a real FAIL into a PASS through an explanation.**

An increment must satisfy its applicable objective criteria before approval.

If tests fail, a review cannot declare the increment complete.

Evidence must clearly distinguish simulated results from operations actually executed.

---

# 10. Continuity and Long-Running Operation

Pello V1 may run locally on Windows.

There is no requirement to host the orchestrator in the cloud or build a dashboard.

It must operate while the computer remains powered on, awake, connected, and has valid authentication and available usage quota.

### Required Capabilities

- Autonomous execution of chained tasks.
- Persistent state.
- Continuation after each increment.
- Session rotation.
- Recovery after restarts.
- Handling SDK interruptions.
- Pausing when usage limits are reached.
- Reconciling uncertain external operations.
- Scheduled reporting.
- Safe stopping.

If a quota is exhausted or connectivity is lost, Pello must preserve state and resume when conditions allow it to continue.

It must not interpret a missing response as proof that an external operation never occurred.

---

# 11. Reporting and Progress Measurement

Pello automatically sends a daily email while active projects exist.

The report must contain:

- Project.
- Overall status.
- Completed features.
- Verified requirements.
- Completed increments.
- Tests executed.
- Published changes.
- Detected errors.
- Completed repairs.
- Blockers.
- Next activities.
- Recorded usage.
- Progress percentage.

The information comes from SQLite, checkpoints, and real evidence.

## 11.1. Progress Percentage

Progress must be tied to the product specification's requirements, not merely the number of increments.

Increments may change during development.

For example, a feature initially divided into two tasks may eventually require five without representing an actual loss of product progress.

Product requirements form the stable reference.

Pello must distinguish between:

- Implemented.
- Tested.
- Integrated.
- Fully verified.

A feature must not be counted as complete merely because the Coder wrote its code.

If the approved scope changes, the change in the progress baseline must be recorded.

## 11.2. Quality and Efficiency Metrics

Inspired by DORA practices, Pello records simple metrics to improve its execution:

- Time required per increment.
- Attempts per increment.
- Percentage of increments approved on the first attempt.
- Failures detected after integration.
- Repair time.
- Regressions.
- Published changes.
- Recovery time after an error.
- Results achieved by the models used.

These metrics help determine whether incremental development is improving speed and reducing errors.

V1 does not require building a DevOps metrics platform or formally reproducing every DORA metric.

---

# 12. Final Product Delivery

Pello must deliver the product actually implemented.

The delivery includes:

1. Final code and workflows.
2. Configured integrations.
3. Created or modified resources.
4. IDs and references for external resources.
5. Publishing status.
6. Tests and results.
7. Evidence of real executions.
8. Verified features.
9. Corrected errors.
10. History and checkpoints.
11. Operational documentation.
12. Dependencies and required configuration.
13. Risks or pending issues.
14. Final report.
15. Identification of workflows whose MCP access should be removed.

The result must clearly indicate one of these states:

**VERIFIED:** The product is functional and complete acceptance has been demonstrated.

**PARTIAL WITH BLOCKERS:** A partial implementation exists, but requirements, permissions, or verification are still missing.

**NOT APPROVED:** The product does not meet the conditions required for acceptance.

A workflow that has been created but not properly tested cannot be declared complete.

A workflow that requires a production webhook cannot be considered fully verified if only a temporary test endpoint was exercised and its actual behavior remains unproven.

---

# 13. Pello V1 Acceptance Criteria

| ID | Capability | Required Evidence |
| --- | --- | --- |
| V1-01 | Interpret a product specification | Extracts requirements and produces a plan without requiring a manually written technical task manifest. |
| V1-02 | Autonomous decomposition | Generates functional increments with dependencies and acceptance criteria. |
| V1-03 | Independent testing | Prepares and protects tests before implementation and runs regression tests. |
| V1-04 | Incremental pipeline | Executes Planner, Coder, Tester, and Reviewer responsibilities across multiple dependent tasks. |
| V1-05 | Autonomous correction | Detects a real error, corrects it, and passes verification. |
| V1-06 | Adaptive escalation | Changes model or reasoning effort when supported by evidence. |
| V1-07 | n8n integration | Creates or modifies a real workflow through the official MCP server in the authorized instance. |
| V1-08 | Autonomous publishing | Publishes an authorized version and verifies its actual state. |
| V1-09 | Real integration testing | Executes and verifies the workflow using the required real mechanism, including production webhooks when applicable. |
| V1-10 | Auxiliary integration | Uses at least one authorized external service and verifies its effects. |
| V1-11 | Change control | Preserves versions and can restore configurations when applicable. |
| V1-12 | Memory and sessions | Resumes development without losing context or repeating approved tasks. |
| V1-13 | Recovery | Identifies uncertain operations and avoids blindly repeating them. |
| V1-14 | Long-running execution | Chains work without manual prompt transfer while resources remain available. |
| V1-15 | Automated reporting | Sends daily emails containing evidence-based progress. |
| V1-16 | MCP permissions | Respects workflow exposure through MCP and does not use alternative access methods to bypass restrictions. |
| V1-17 | Budgets | Stops tasks upon reaching mandatory limits and preserves state. |
| V1-18 | Requirement validation | Identifies contradictions, records assumptions, and continues with non-blocked work. |
| V1-19 | Independent review | Reviewer uses a separate evaluation context and does not modify code. |
| V1-20 | Complete delivery | Delivers a functional business automation product, published when appropriate, tested, and documented. |
| V1-21 | STOP and recovery | Stops new operations and resumes after reconciling previous state, without disabling delivered workflows. |
| V1-22 | Production test-data management | Identifies and cleans up or documents test resources created. |
| V1-23 | MCP access lifecycle | Works on MCP-enabled workflows, records new IDs, and supports delivery of operational workflows without retaining development access. |

## 13.1. Final V1 Acceptance Test

The final acceptance test uses a product specification representative of a real business automation project.

The infrastructure and MCP connection are prepared beforehand.

The test must demonstrate that Pello:

1. Understands the specification.
2. Autonomously decomposes the work.
3. Defines contracts and prepares tests.
4. Implements multiple increments.
5. Creates and modifies resources through n8n MCP.
6. Records IDs of newly created workflows.
7. Publishes workflows when required by the integration.
8. Verifies their behavior through controlled real operations.
9. Detects and corrects at least one real failure.
10. Preserves context after an interruption.
11. Sends automated reports.
12. Finishes with a functional product and a verifiable final report.
13. Identifies workflows ready to have MCP access removed without unpublishing them.

There is no requirement to use a specific industry as the reference project.

The test must demonstrate general capability, not a chatbot designed for one particular example.

---

# 14. V1 Scope and Constraints

- Pello initially runs on Windows.
- Its core is implemented in Python.
- It uses SQLite, Git, and durable files.
- It uses the Codex SDK and compatible tools.
- It works with a single n8n instance hosted on Railway.
- Its primary n8n connection uses the official MCP server.
- I manually configure the connection in `config.toml`.
- I enable MCP access to workflows requiring development or maintenance.
- Delivered workflows may remain published while their MCP access is disabled.
- Pello may create new workflows through MCP.
- Pello automatically records IDs of newly created workflows.
- Pello may publish workflows within the authorized scope.
- A second DEV instance is not required.
- Duplicating workflows to separate development and production is not required.
- A custom n8n proxy is not a V1 requirement.
- No alternative administrative access is added that would bypass MCP restrictions.
- It maintains versions and evidence to control changes.
- It uses real tests with controlled external effects.
- It does not require four permanent AI processes.
- It does not require fixed models for every invocation.
- It does not need a graphical dashboard.
- It does not require training or fine-tuning model weights.
- It does not need cloud infrastructure dedicated to hosting the orchestrator.
- It does not depend on mandatory ChatGPT Chat integration as the Reviewer.
- It does not require universal compatibility with every existing tool.
- It cannot assume unlimited Codex usage quotas.
- It cannot promise to reverse irreversible external effects.
- It does not change product scope without authorization.
- It does not claim real implementations based on simulated results.

Policies for models, time limits, attempts, consumption, reviews, sessions, and reports must remain configurable within controlled boundaries.

---

# 15. Guiding Development Principle

Every Pello implementation must contribute to the following capability:

**Receive a product specification → understand it → plan → decompose → define contracts → prepare tests → code → test → review → correct → integrate → publish when appropriate → continue → report → deliver a working product.**

Incremental development is the primary mechanism for preserving context and reducing the scope of errors.

External tools allow Pello to produce real systems rather than merely generating files.

Persistent memory allows work to continue.

Independent testing and reviews allow results to be verified.

Version control, MCP permissions, and operational limits allow autonomous work on an authorized production instance.

**Pello V1 is complete when it can receive a product specification and transform its requirements into a real, functional, verifiable automation with minimal human technical intervention after the environment has been prepared.**

---

## Technical References

- DORA — Working in small batches: https://dora.dev/capabilities/working-in-small-batches/
- DORA — Continuous delivery: https://dora.dev/capabilities/continuous-delivery/
- n8n — Connect to n8n MCP server: https://docs.n8n.io/connect/connect-to-n8n-mcp-server
- n8n — MCP server tools reference: https://docs.n8n.io/connect/connect-to-n8n-mcp-server/mcp-server-tools-reference
- n8n — MCP client connection examples: https://docs.n8n.io/connect/connect-to-n8n-mcp-server/mcp-client-examples
- n8n — Save and publish workflows: https://docs.n8n.io/workflows/publish/
- n8n — Webhook node: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/

**End of Pello V1 Product Specification — Version 1.3.**
