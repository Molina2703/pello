"""Validated Phase 2 exchanges. Agent claims never substitute for observations."""
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=6000)]
Identifier = Annotated[str, StringConstraints(pattern=r'^[A-Za-z0-9][A-Za-z0-9_-]{0,95}$')]
Action = Literal['CONTINUE', 'REPAIR', 'COMPLETE', 'BLOCKED', 'NEEDS_HUMAN']


class Message(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class TaskDefinition(Message):
    task_id: Identifier
    objective: Text
    implementation_instruction: Text
    relevant_context: list[Text] = Field(max_length=8)
    acceptance_criteria: list[Text] = Field(min_length=1, max_length=20)
    completion_criteria: list[Text] = Field(min_length=1, max_length=20)
    constraints: list[Text] = Field(min_length=1, max_length=12)
    depends_on: list[Identifier] = Field(max_length=8)


class SupervisorDecision(Message):
    project_id: Identifier
    task_id: Identifier
    decision: Action
    tasks: list[TaskDefinition] = Field(max_length=8)
    reasoning_summary: Text
    next_action: Text

    @model_validator(mode='after')
    def sequential_plan(self):
        previous = set()
        for task in self.tasks:
            if task.task_id in previous or not set(task.depends_on) <= previous:
                raise ValueError('Task IDs must be unique; dependencies must precede dependants')
            previous.add(task.task_id)
        return self


class ExecutorReply(Message):
    project_id: Identifier
    task_id: Identifier
    execution_summary: Text
    files_modified: list[Text] = Field(max_length=50)
    errors: list[Text] = Field(max_length=12)
    evidence_paths: list[Text] = Field(max_length=20)


class ExecutionResult(Message):
    project_id: Identifier
    task_id: Identifier
    executor_session_id: Text
    execution_status: Literal['completed', 'failed', 'interrupted']
    files_modified: list[Text]
    claimed_files_modified: list[Text]
    execution_summary: Text
    errors: list[Text]
    evidence_paths: list[Text]
    usage_metadata: dict


class VerificationResult(Message):
    project_id: Identifier
    task_id: Identifier
    verification_status: Literal['PASSED', 'FAILED', 'BLOCKED']
    tests_executed: int = Field(ge=0)
    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    skipped: int = Field(ge=0)
    evidence_paths: list[Text]
    error_summary: str = Field(max_length=12000)

    @model_validator(mode='after')
    def counts_match(self):
        if self.passed + self.failed + self.skipped != self.tests_executed:
            raise ValueError('Verification counts do not match')
        if self.verification_status == 'PASSED' and (
                not self.tests_executed or self.failed or self.skipped):
            raise ValueError('Passing verification requires executed tests with no failures/skips')
        return self


def parse_response(model, text):
    # Reject markdown fences, trailing prose, unknown keys and missing fields.
    if len(text.encode('utf-8')) > 64000:
        raise ValueError('Structured response exceeds 64KB')
    return model.model_validate_json(text)


def correlate(message, project_id, task_id=None):
    if message.project_id != project_id or (task_id is not None and message.task_id != task_id):
        raise ValueError('Message project/task correlation mismatch')
