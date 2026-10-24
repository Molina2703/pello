"""Owner-controlled increments and small, correlated model exchanges."""
from pathlib import PurePosixPath
import re
from typing import Literal
from pydantic import Field, model_validator
from .messages import Message, Text, Identifier


def relative_path(value):
    path = PurePosixPath(value)
    if not value or '\\' in value or ':' in value or path.is_absolute() or any(p in ('..', '.git') for p in path.parts):
        raise ValueError('Expected a relative path inside the project')
    return value


class Increment(Message):
    task_id: Identifier
    specification: Text
    inputs: list[Text] = Field(min_length=1, max_length=12)
    outputs: list[Text] = Field(min_length=1, max_length=12)
    components: list[Text] = Field(min_length=1, max_length=12)
    acceptance_criteria: list[Text] = Field(min_length=1, max_length=20)
    depends_on: list[Identifier] = Field(max_length=8)
    suite: Text
    expected_tests: int = Field(ge=1, le=500)
    risk: Literal['routine', 'high'] = 'routine'

    @model_validator(mode='after')
    def paths(self):
        relative_path(self.suite)
        for component in self.components:
            relative_path(component)
        return self


class ToolBinding(Message):
    tool: Identifier
    environment: Literal['local', 'development', 'staging', 'production']
    connection_ref: str = Field(max_length=200)
    allowed_operations: list[Text] = Field(max_length=12)
    resource_ids: list[Text] = Field(max_length=12)
    verification: Text
    permission_boundary: Text = 'Only the declared project resources and operations'
    enabled: bool


class PipelineManifest(Message):
    architecture_constraints: list[Text] = Field(min_length=1, max_length=12)
    tools: list[ToolBinding] = Field(max_length=12)
    increments: list[Increment] = Field(min_length=1, max_length=8)

    @model_validator(mode='after')
    def graph_and_tools(self):
        previous = set()
        for task in self.increments:
            if task.task_id in previous or len(set(task.depends_on)) != len(task.depends_on) or not set(task.depends_on) <= previous:
                raise ValueError('Unique increments must follow their dependencies')
            previous.add(task.task_id)
        for tool in self.tools:
            if tool.enabled and (tool.tool not in ('python', 'git') or tool.environment != 'local' or tool.connection_ref or tool.resource_ids):
                raise ValueError('Phase 3A enables only local Python/Git; external tools are declarations only')
            if tool.enabled and not set(tool.allowed_operations) <= ({'run_tests', 'implement'} if tool.tool == 'python' else {'inspect', 'checkpoint'}):
                raise ValueError('Unsupported local tool operation')
            if tool.connection_ref and not re.fullmatch(r'(connection|vault|envref):[A-Za-z0-9_./-]{1,100}', tool.connection_ref):
                raise ValueError('Connections must use non-secret references, never credential values')
        return self


class PlannedIncrement(Message):
    task_id: Identifier
    objective: Text
    implementation_instruction: Text


class PipelinePlan(Message):
    project_id: Identifier
    architecture: list[Text] = Field(min_length=1, max_length=12)
    tasks: list[PlannedIncrement] = Field(min_length=1, max_length=8)
    reasoning_summary: Text


class IncrementReview(Message):
    project_id: Identifier
    task_id: Identifier
    attempt: int = Field(ge=1)
    verdict: Literal['PASS', 'FAIL', 'BLOCKED']
    diagnosis: Literal['none', 'implementation', 'specification', 'integration', 'infrastructure']
    feedback: Text


class PipelinePolicy(Message):
    max_attempts: int = Field(default=2, ge=1, le=10)
    max_turns: int = Field(default=12, ge=1, le=60)
    review: Literal['every_increment', 'final'] = 'every_increment'
    routine_model: str = 'gpt-6-luna'
    advanced_model: str = 'gpt-6.1-sol'
    routine_effort: Literal['low', 'medium', 'high'] = 'low'
    advanced_effort: Literal['low', 'medium', 'high'] = 'medium'

    @model_validator(mode='after')
    def allowed_models(self):
        allowed = {'gpt-6-luna', 'gpt-6-sol', 'gpt-6.1-sol'}
        if self.routine_model not in allowed or self.advanced_model not in allowed:
            raise ValueError('Only explicitly allowed Luna/Sol models; Astra and paid API are prohibited')
        return self
