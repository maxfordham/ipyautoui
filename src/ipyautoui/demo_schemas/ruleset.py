from enum import Enum
from pydantic import BaseModel, Field
from ipyautoui import AutoUi

URL_REVIT_FILTERS = "https://help.autodesk.com/view/RVT/2023/ENU/?guid=GUID-400FD74B-00E0-4573-B3AC-3965E65CBBDB"


def html_link(url, description):
    return f'<a href="{url}" target="blank" >{description}</a>'


class RuleSetType(str, Enum):
    """how the rules logically multiply. Must be `AND` for schedules"""

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
        title="Categories",  # TODO: this is pydantic bug (should generate title from field name)
        description="Revit MEP categories to filter by (i.e. revit object must belong to categories defined here). If empty, all categories are included.",
    )
    parameter: str
    operator: RevitOperatorsEnum
    value: str = Field(
        "",
        description="Value to filter by. Evaluates to the appropriate type. Leave empty if none required (e.g. has value operator)",
    )


class ScheduleRuleSet(BaseModel):

    set_type: RuleSetType = Field(default=RuleSetType.AND, const=True, disabled=True)
    rules: list[Rule] = Field(
        description="""
rules return a boolean for the logical evaluation defined below for every item within the categories defined
"""
    )


ScheduleRuleSet.__doc__ = """A set of rules that defines what equipment specifications will appear in a given schedule.
    Rules must evaluate to True for the item to be included in a schedule
    Analogous to filter rules in 
    """ + html_link(
    URL_REVIT_FILTERS, "Revit."
)

# class RuleSet(BaseModel):
#     set_type: RuleSetType
#     rules: list[ty.Union[Rule, ty.ForwardRef("RuleSet")]]

# RuleSet.update_forward_refs()
# ^ TODO: add support for nested rulesets with ty.Union[Rule, RuleSet]...
