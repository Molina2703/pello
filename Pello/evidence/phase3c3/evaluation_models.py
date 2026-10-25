"""Independent held-out evaluation data; never imported by product Planner."""
from typing import Literal
from pydantic import Field
from athis_autopilot.messages import Message

class RubricCriterion(Message):
    criterion_id: str
    severity: Literal['critical','minor']
    area: Literal['requirements','issues','architecture','dependencies','increments','contracts',
                  'authorization','models','persistence','test_claims']
    source_quote: str
    expected_planning_outcome: str = Field(max_length=1500)
    failure_condition: str = Field(max_length=1000)

class HeldOutFixture(Message):
    evaluation_id: str
    product_name: str
    specification_markdown: str = Field(min_length=2200,max_length=8500)
    novelty_rationale: str = Field(max_length=2000)
    rubric: list[RubricCriterion] = Field(min_length=20,max_length=30)
    independent_capabilities: list[str] = Field(min_length=2,max_length=5)
    minimum_critical_pass_fraction: Literal[1.0]
    minimum_total_pass_fraction: Literal[0.9]

class CriterionResult(Message):
    criterion_id: str
    verdict: Literal['PASS','FAIL','BLOCKED']
    evidence_references: list[str] = Field(min_length=1,max_length=8)
    rationale: str = Field(max_length=1200)

class SemanticVerdict(Message):
    verdict: Literal['PASS','FAIL','BLOCKED']
    criteria: list[CriterionResult] = Field(min_length=20,max_length=30)
    critical_failures: list[str] = Field(max_length=20)
    minor_findings: list[str] = Field(max_length=20)
    reproduction: list[str] = Field(max_length=15)
    remediation: list[str] = Field(max_length=15)
    explanation: str = Field(max_length=3000)
