from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RoleRef(BaseModel):
    role_name: Optional[str]
    tasks_used_in_simulation: List[str] = Field(default_factory=list)


class CoveredByRole(BaseModel):
    entity_id: str
    covers_tasks: List[str] = Field(default_factory=list)


class CoverageEvaluation(BaseModel):
    covered_by_roles: List[CoveredByRole] = Field(default_factory=list)
    control_modifier: Optional[float] = 1.0
    execution_factor: Optional[float] = 1.0


class RequiredTask(BaseModel):
    task_id: str
    weight: float = 0.0


class Scenario(BaseModel):
    id: str
    name: str
    required_tasks: List[RequiredTask] = Field(default_factory=list)
    coverage_evaluation: CoverageEvaluation = Field(default_factory=CoverageEvaluation)


class PlanData(BaseModel):
    version: Optional[str]
    organization: Optional[str]
    role_task_coverage_reference: Dict[str, RoleRef] = Field(default_factory=dict)
    scenarios: List[Scenario] = Field(default_factory=list)


def validate_plan(data: dict) -> PlanData:
    """Validate and parse plan JSON into Pydantic models.

    Raises `pydantic.ValidationError` on failure.
    """
    # model_validate is preferred in Pydantic v2, parse_obj is deprecated
    return PlanData.model_validate(data)
