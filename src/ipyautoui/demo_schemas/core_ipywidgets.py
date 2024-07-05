"""
An example schema definition that demonstrates the current capability of the AutoUi class
"""

import typing as ty
import annotated_types
from enum import Enum
from pydantic import StringConstraints, Field, conint, confloat, ConfigDict
from ipyautoui.basemodel import BaseModel
from typing_extensions import Annotated
from enum import IntEnum


class FruitEnum(str, Enum):
    """fruit example."""

    apple = "apple"
    pear = "pear"
    banana = "banana"
    orange = "orange"


class Number(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3


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


class CoreIpywidgets(BaseModel):
    """this is a test UI form to demonstrate how pydantic class can  be used to generate an ipywidget input form.
    only simple datatypes used (i.e. not lists/arrays or objects)
    """

    int_slider_req: Annotated[int, Field(ge=1, le=3)] = Field(2, description="a slider")
    int_slider_nullable: ty.Optional[Annotated[int, Field(ge=1, le=3)]] = None
    int_slider: Annotated[int, Field(ge=1, le=3)] = 2
    int_text_req: int
    int_text_nullable: ty.Optional[int]
    int_range_slider: tuple[conint(ge=0, le=4), conint(ge=0, le=4)] = Field(
        default=(0, 3)
    )
    int_range_slider_disabled: tuple[conint(ge=0, le=4), conint(ge=0, le=4)] = Field(
        default=(0, 3), json_schema_extra=dict(json_schema_extra=dict(disabled=True))
    )
    float_slider: float = Field(default=2.2, ge=1, le=3)
    float_text: float = 2.2
    float_text_with_unit: float = Field(default=2.2, json_schema_extra=dict(unit="mm"))
    float_text_locked: float = Field(default=2.2, json_schema_extra=dict(disabled=True))
    float_range_slider: tuple[confloat(ge=0, le=4), confloat(ge=0, le=4)] = Field(
        default=(0, 2.2)
    )
    checkbox: bool = Field(
        default=True, title="boolean checkbox", description="a checkbox"
    )
    dropdown: ty.Optional[FruitEnum] = None
    dropdown_int: Number = Field(default=Number.ONE)  #
    dropdown_int_optional: ty.Optional[Number] = Field(default=Number.ONE)  #
    combobox: str = Field("apple", examples=FruitEnum._member_names_)
    combobox1: ty.Union[str, FruitEnum] = Field("apple")  # TODO: make this work
    dropdown_edge_case: FruitEnum = Field(
        title="dropdwon FruitEnum with metadata",
        default=FruitEnum.apple,
        description="updated description",
    )
    dropdown_simple: str = Field(
        default="asd", json_schema_extra=dict(enum=["asd", "asdf"])
    )
    text: str = Field(default="adsf", description="a description about my string")
    text_short: Annotated[str, StringConstraints(min_length=0, max_length=20)] = (
        "short text"
    )
    textarea: Annotated[str, StringConstraints(min_length=0, max_length=800)] = Field(
        "long text " * 50, description="long text field"
    )
    select_multiple: ty.List[FruitEnum] = Field(
        (FruitEnum.apple,), description="a short select multiple list"
    )
    select_multiple_nullable: ty.Optional[ty.List[FruitEnum]] = Field(
        None, description="a short nullable select multiple list"
    )
    tags_input: ty.List[LongEnum] = Field(
        (LongEnum.a,), description="a long select multiple list"
    )
    tags_input_nullable: ty.Optional[ty.List[LongEnum]] = Field(
        (LongEnum.a,), description="a long nullable select multiple list"
    )

    model_config = ConfigDict(json_schema_extra=dict(show_raw=True))
