from ipyautoui.basemodel import BaseModel
from pydantic import Field, conint, constr
import typing as ty

DATAGRID_TEST_VALUE = [
    {
        "string": "how long",
        "integer": 1,
        "floater": 3.14,
        "something_else": 324,
    },
    # {"string": "update", "integer": 4, "floater": 3.12344, "something_else": 123},
    # {"string": "evening", "integer": 5, "floater": 3.14, "something_else": 235},
    # {"string": "morning", "integer": 5, "floater": 3.14, "something_else": 12},
    # {"string": "number", "integer": 3, "floater": 3.14, "something_else": 123},
]


class DataFrameCols(BaseModel):
    string: str = Field("string", column_width=200)
    integer: int = Field(1)
    floater: float = Field(3.1415, column_width=70)
    something_else: float = Field(324, column_width=100)


class EditableGrid(BaseModel):
    __root__: ty.List[DataFrameCols] = Field(
        default=DATAGRID_TEST_VALUE,
        # default_factory=lambda: DATAGRID_TEST_VALUE, # TODO: AutoUi isn't getting data when set using default_factory. make this work!
        format="DataFrame",
        global_decimal_places=2,
    )
