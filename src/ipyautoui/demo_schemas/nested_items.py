from pydantic import Field, conint, constr
from ipyautoui.basemodel import BaseModel


class NestedObject(BaseModel):
    """description in docstring"""

    string1: str = Field(default="adsf", description="a description about my string")
    int_slider1: conint(ge=0, le=3) = 2
    int_text1: int = 1


class RecursiveNest(BaseModel):
    """description in RecursiveNest docstring"""

    string1: str = Field(default="adsf", description="a description about my string")
    int_slider1: conint(ge=1, le=3) = 2
    int_text1: int = 1
    nested: NestedObject


class Nested(BaseModel):
    """demonstrates nested objects"""

    nested: NestedObject
    recursive_nest: RecursiveNest
    array_simple: list[str]
    arrar_objects: list[NestedObject]
