from ipyautoui.basemodel import BaseModel
from pydantic import Field, conint, constr
import typing as ty

DATAGRID_TEST_VALUE = [
    {
        "string": "important string",
        "integer": 1,
        "floater": 3.14,
        "something_else": 324,
    },
    {"string": "update", "integer": 4, "floater": 3.12344, "something_else": 123},
    {"string": "evening", "integer": 5, "floater": 3.14, "something_else": 235},
    {"string": "morning", "integer": 5, "floater": 3.14, "something_else": 12},
    {"string": "number", "integer": 3, "floater": 3.14, "something_else": 123},
]


class DataFrameCols(BaseModel):
    string: str = Field("string", json_schema_extra=dict(column_width=200))
    integer: int = Field(1)
    floater: float = Field(3.1415, json_schema_extra=dict(column_width=70))
    something_else: float = Field(324, json_schema_extra=dict(column_width=100))


class NestedEditableGrid(BaseModel):
    title: str = "My editable Dataframe"
    reference: ty.Optional[str] = None  # TODO: this creates formatting issue
    grid: ty.List[DataFrameCols] = Field(
        default=DATAGRID_TEST_VALUE,
        json_schema_extra=dict(format="DataFrame", global_decimal_places=2),
    )
