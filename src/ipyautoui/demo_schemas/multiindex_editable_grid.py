from ipyautoui.basemodel import BaseModel
from pydantic import Field, RootModel, ConfigDict
import typing as ty

DATAGRID_TEST_VALUE = [
    {
        "string": "how long",
        "integer": 1,
        "floater": 3.14,
        "something_else": 324,
    },
]


# class DataFrameCols(BaseModel):
#     string: str = Field("string", title=("string", "string"), json_schema_extra=dict(column_width=200))
#     integer: int = Field(1, title=("number", "integer"))
#     floater: float = Field(3.1415,title=("number", "integer"), json_schema_extra=dict(column_width=70))
#     something_else: float = Field(324,title=("number", "something_else"), json_schema_extra=dict(column_width=100))
# NOTE: should it work like this ^


class DataFrameCols(BaseModel):
    string: str = Field(
        "string", json_schema_extra=dict(column_width=200, section="string")
    )
    integer: int = Field(1, json_schema_extra=dict(column_width=200, section="number"))
    floater: float = Field(
        3.1415, json_schema_extra=dict(column_width=70, section="number")
    )
    something_else: float = Field(
        324, json_schema_extra=dict(column_width=100, section="number")
    )


class MultiIndexEditableGrid(RootModel):
    root: ty.List[DataFrameCols]
    model_config = ConfigDict(
        json_schema_extra=dict(
            default=DATAGRID_TEST_VALUE,
            # default_factory=lambda: DATAGRID_TEST_VALUE, # TODO: AutoUi isn't getting data when set using default_factory. make this work!
            format="DataFrame",
            warn_on_delete=True,  # TODO: this isn't being passed
            global_decimal_places=2,
            datagrid_index_name=("section", "title"),
        )
    )
