from ipyautoui.basemodel import BaseModel
from pydantic import Field, conint, constr, RootModel
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


EditableGrid = RootModel[ty.List[DataFrameCols]]
EditableGrid.__pydantic_extra__ = dict(
    default=DATAGRID_TEST_VALUE,
    # default_factory=lambda: DATAGRID_TEST_VALUE, # TODO: AutoUi isn't getting data when set using default_factory. make this work!
    format="DataFrame",
    warn_on_delete=True,  # TODO: this isn't being passed
    global_decimal_places=2,
)
