from typing import Dict, Optional, Any, List
from aidial_sdk.pydantic_v1 import Field
from aidial_sdk.utils.pydantic import ExtraForbidModel


class ActionArgumentSchema(ExtraForbidModel):
    type: str = Field(..., description="The type of the argument, e.g., 'string', 'number'")
    description: Optional[str] = Field(None, description="A brief description of the argument")
    default: Optional[Any] = Field(None, description="The default value of the argument, if any")
    value: Optional[Any] = Field(None, description="The actual value of the argument, when set")


class Action(ExtraForbidModel):
    name: str = Field(..., description="The name of the action button")
    action_id: str = Field(..., description="The unique identifier for the action")
    required: List[str] = Field(default_factory=list, description="List of required argument names")
    label: Optional[str] = Field(None, description="The label for the action button")
    description: Optional[str] = Field(None, description="A brief description of what the action does")
    parameters: Optional[Dict[str, ActionArgumentSchema]] = Field(None, description="List of arguments required to call the action")
