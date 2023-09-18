from pydantic import Field, RootModel
from ipyautoui.basemodel import BaseModel
from typing_extensions import Annotated
import typing as ty


class NestedObject(BaseModel):
    """description in docstring"""

    string1: str = Field(default="adsf", description="a description about my string")
    int_slider1: Annotated[int, Field(ge=0, le=3)] = 2
    int_text1: int = 1


class MyString(RootModel):
    root: str = Field(description="checks", default="check kitchen", pattern="check*")


class ArrayWithUnionType(BaseModel):
    auto_simple: list[str]
    auto_custom_str: list[MyString]
    auto_object: list[NestedObject]
    auto_anyof: list[ty.Union[NestedObject, str]] = Field(
        description="NOT SUPPORTED YET"
    )
