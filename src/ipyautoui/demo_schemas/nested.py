from pydantic import Field, constr
from ipyautoui.basemodel import BaseModel
from typing_extensions import Annotated
from enum import Enum


class LongEnum(str, Enum):
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    e = "e"
    f = "f"
    g = "g"
    h = "h"
    i = "i"
    j = "j"
    k = "k"
    l = "l"
    m = "m"
    n = "n"
    o = "o"
    p = "p"


class NestedObject(BaseModel):
    """description in docstring"""

    string1: str = Field(default="adsf", description="a description about my string")
    int_slider1: Annotated[int, Field(ge=0, le=3)] = 2
    int_text1: int = 1
    tags: list[LongEnum] = (LongEnum.a,)


class RecursiveNest(BaseModel):
    """description in RecursiveNest docstring"""

    string1: str = Field(default="adsf", description="a description about my string")
    int_slider1: Annotated[int, Field(ge=1, le=3)] = 2
    int_text1: int = 1
    nested: NestedObject


class Nested(BaseModel):
    """demonstrates nested objects"""

    nested: NestedObject
    recursive_nest: RecursiveNest
    array_simple: list[str]
    array_objects: list[NestedObject]
    nullable_list: list[str] = None
    nullable_object: NestedObject = None
