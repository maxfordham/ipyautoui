from pydantic import Field
from ipyautoui.basemodel import BaseModel
from typing_extensions import Annotated


class NestedObject(BaseModel):
    """description in docstring"""

    string1: str = Field(default="adsf", description="a description about my string")
    int_slider1: Annotated[int, Field(ge=0, le=3)] = 2
    int_text1: int = 1


class ArrayObjectDataframe(BaseModel):
    auto_array: list[str]
    auto_object: NestedObject
    edit_grid: list[NestedObject] = Field(json_schema_extra=dict(format="dataframe"))
