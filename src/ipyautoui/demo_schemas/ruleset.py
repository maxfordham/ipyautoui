from enum import Enum
import pathlib
import json
from pydantic import BaseModel, Field
import typing as ty
from ipyautoui.constants import DIR_MODULE


class RuleSetType(str, Enum):
    AND: str = "AND"
    OR: str = "OR"


class StrEnum(str, Enum):
    pass


p = DIR_MODULE / "demo_schemas" / "revit_mep_categories.json"
RevitCategoriesEnum = StrEnum("RevitCategoriesEnum", json.loads(p.read_text()))


p = DIR_MODULE / "demo_schemas" / "revit_operators.json"
RevitOperatorsEnum = StrEnum("RevitOperatorsEnum", json.loads(p.read_text()))


class Rule(BaseModel):
    categories: list[RevitCategoriesEnum] = Field(
        description="Revit MEP categories to filter by. If empty, all categories are included."
    )
    parameter: str
    operator: RevitOperatorsEnum
    value: str = Field(
        "",
        description="Value to filter by. Evaluates to the appropriate type. Leave empty if none required (e.g. has value operator)",
    )


class RuleSet(BaseModel):
    set_type: RuleSetType
    rules: list[ty.Union[Rule, ty.ForwardRef("RuleSet")]]


RuleSet.update_forward_refs()


class ScheduleRuleSet(BaseModel):
    set_type: RuleSetType = Field(default=RuleSetType.AND, const=True)
    rules: list[Rule]
