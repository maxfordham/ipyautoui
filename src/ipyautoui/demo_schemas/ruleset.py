from enum import Enum
from pydantic import BaseModel, Field

class RuleSetType(str, Enum):
    AND: str = "AND"
    OR: str = "OR"


class StrEnum(str, Enum):
    pass


RevitCategoriesEnum = StrEnum(
    "RevitCategoriesEnum",
    {
        "OST_AnalyticSpaces": "Analytical Spaces",
        "OST_DuctTerminal": "Air Terminals",
        "OST_ElectricalEquipment": "Electrical Equipment",
        "OST_ElectricalFixtures": "Electrical Fixtures",
        "OST_MEPAnalyticalAirLoop": "Air Systems",
        "OST_MEPAnalyticalWaterLoop": "Water Loops",
        "OST_MEPSpaces": "Spaces",
        "OST_PipeAccessory": "Pipe Accessories",
        "OST_PipeCurves": "Pipes",
        "OST_PipeFitting": "Pipe Fittings",
        "OST_PipeInsulations": "Pipe Insulations",
        "OST_PipingSystem": "Piping Systems",
        "OST_PlumbingFixtures": "Plumbing Fixtures",
        "OST_Sprinklers": "Sprinklers",
    },
)

RevitOperatorsEnum = StrEnum(
    "RevitOperatorsEnum",
    {
        "BeginsWith": "begins with",
        "Contains": "contains",
        "EndsWith": "ends with",
        "Equals": "equals",
        "GreaterOrEqual": "is greater than or equal to",
        "Greater": "is greater than",
        "HasNoValueParameter": "has no value",
        "HasValueParameter": "has value",
        "IsAssociatedWithGlobalParameter": "?",
        "IsNotAssociatedWithGlobalParameter": "?",
        "LessOrEqual": "is less than or equal to",
        "Less": "is less than",
        "NotBeginsWith": "does not begin with",
        "NotContains": "does not contain",
        "NotEndsWith": "does not end with",
        "NotEquals": "dont not equal",
        "SharedParameterApplicable": "?",
    },
)


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


class ScheduleRuleSet(BaseModel):
    set_type: RuleSetType = Field(default=RuleSetType.AND, const=True)
    rules: list[Rule]


# class RuleSet(BaseModel):
#     set_type: RuleSetType
#     rules: list[ty.Union[Rule, ty.ForwardRef("RuleSet")]]

# RuleSet.update_forward_refs()

# ^ TODO: add support for nested rulesets with ty.Union[Rule, RuleSet]...
