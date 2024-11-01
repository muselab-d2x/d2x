from pydantic import BaseModel, Field, root_validator
from typing import List, Optional, Dict, Any, Union

class CommonBaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

class CollectStep(CommonBaseModel):
    key: str = Field(..., description="Key for the collect step")
    type: str = Field(..., description="Type of the collect step, e.g., soql or metadata")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Configuration options for the collect step")

class CheckAction(CommonBaseModel):
    key: str = Field(..., description="Key for the check action")
    type: str = Field(..., description="Type of the check action, e.g., info, warning, error, or step_modifier")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Configuration options for the check action")

class CollectPhase(CommonBaseModel):
    steps: List[CollectStep] = Field(..., description="List of collect steps")

class CheckPhase(CommonBaseModel):
    actions: List[CheckAction] = Field(..., description="List of check actions")

class RunStep(CommonBaseModel):
    step_type: str = Field(..., description="Type of the run step, e.g., sf, cci, or d2x")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Configuration options for the run step")

    @root_validator(pre=True)
    def validate_step_type(cls, values):
        step_type = values.get('step_type')
        if step_type not in ['sf', 'cci', 'd2x']:
            raise ValueError('Invalid step_type. Must be one of: sf, cci, d2x')
        return values

class RunPhase(CommonBaseModel):
    dependencies: Optional[List[str]] = Field(default=None, description="List of dependencies to install")
    deploy_metadata: Optional[List[str]] = Field(default=None, description="List of metadata components to deploy")
    install_packages: Optional[List[str]] = Field(default=None, description="List of packages to install")
    setup_steps: Optional[List[RunStep]] = Field(default=None, description="List of setup steps to perform")
    config_steps: Optional[List[RunStep]] = Field(default=None, description="List of configuration steps to perform")
    data_steps: Optional[List[RunStep]] = Field(default=None, description="List of data steps to perform")
    testing_steps: Optional[List[RunStep]] = Field(default=None, description="List of testing steps to perform")

class Plan(CommonBaseModel):
    name: str = Field(..., description="Name of the plan")
    description: Optional[str] = Field(default=None, description="Description of the plan")
    collect: CollectPhase
    check: CheckPhase
    run: RunPhase
