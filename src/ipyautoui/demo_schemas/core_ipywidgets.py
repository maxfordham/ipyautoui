"""
An example schema definition that demonstrates the current capability of the AutoUi class
"""
import typing as ty
import annotated_types
from enum import Enum
from pydantic import StringConstraints, Field, conint, confloat
from ipyautoui.basemodel import BaseModel
import pandas as pd
from pathlib import PurePosixPath
from typing_extensions import Annotated


class FruitEnum(str, Enum):
    """fruit example."""

    apple = "apple"
    pear = "pear"
    banana = "banana"
    orange = "orange"


class CoreIpywidgets(BaseModel):
    """this is a test UI form to demonstrate how pydantic class can be used to generate an ipywidget input form.
    only simple datatypes used (i.e. not lists/arrays or objects)
    """

    int_slider_req: Annotated[int, Field(ge=1, le=3)]
    int_slider_nullable: Annotated[int, Field(ge=1, le=3)] = None
    int_slider: Annotated[int, Field(ge=1, le=3)] = 2
    int_text: int = 1
    int_range_slider: tuple[conint(ge=0, le=4), conint(ge=0, le=4)] = Field(
        default=(0, 3)
    )
    int_range_slider_disabled: tuple[conint(ge=0, le=4), conint(ge=0, le=4)] = Field(
        default=(0, 3), disabled=True
    )
    float_slider: float = Field(default=2.2, ge=1, le=3)
    float_text: float = 2.2
    float_text_locked: float = Field(default=2.2, disabled=True)
    float_range_slider: tuple[confloat(ge=0, le=4), confloat(ge=0, le=4)] = Field(default=(0, 2.2))
    checkbox: bool = True
    dropdown: FruitEnum = None
    combobox: str = Field("apple", examples=FruitEnum._member_names_)
    # combobox1: ty.Union[str, FruitEnum] = Field("apple") # TODO: make this work
    dropdown_edge_case: FruitEnum = Field(
        title="FruitEnum with metadata",
        default=FruitEnum.apple,
        description="updated description",
    )
    dropdown_simple: str = Field(default="asd", enum=["asd", "asdf"])
    text: str = Field(default="adsf", description="a description about my string")
    text_short: Annotated[
        str, StringConstraints(min_length=0, max_length=20)
    ] = "short text"
    text_area: Annotated[str, StringConstraints(min_length=0, max_length=800)] = Field(
        "long text " * 50, description="long text field"
    )
