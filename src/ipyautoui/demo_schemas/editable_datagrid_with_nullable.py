from ipyautoui.basemodel import BaseModel
from pydantic import Field, RootModel, ConfigDict
import typing as ty

DATAGRID_TEST_VALUE = [
    {
        "string": "how long",
        "nullable_string": None,
        "integer": 1,
        "floater": 3.14,
        "something_else": 324,
    },
]


class DataFrameCols(BaseModel):
    string: str = Field("string", json_schema_extra=dict(column_width=200))
    nullable_string: ty.Optional[str] = Field(
        None, json_schema_extra=dict(column_width=200)
    )
    integer: int = Field(1)
    floater: float = Field(3.1415, json_schema_extra=dict(column_width=70))
    something_else: float = Field(324, json_schema_extra=dict(column_width=100))


class EditableGridWithNullable(RootModel):
    root: ty.List[DataFrameCols]
    model_config = ConfigDict(
        json_schema_extra=dict(
            default=DATAGRID_TEST_VALUE,
            # default_factory=lambda: DATAGRID_TEST_VALUE, # TODO: AutoUi isn't getting data when set using default_factory. make this work!
            format="DataFrame",
            warn_on_delete=True,  # TODO: this isn't being passed
            global_decimal_places=2,
        )
    )
