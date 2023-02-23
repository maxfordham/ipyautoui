"""
An example schema definition that demonstrates the current capability of the AutoUi class
"""
import typing as ty
from enum import Enum
from pydantic import Field, conint, constr
from ipyautoui.basemodel import BaseModel
import pandas as pd
from pathlib import PurePosixPath


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

    int_slider_req: conint(ge=1, le=3)
    int_slider_nullable: conint(ge=1, le=3) = None
    int_slider: conint(ge=1, le=3) = 2
    int_text: int = 1
    int_range_slider: tuple[int, int] = Field(default=(0, 3), ge=0, le=4)
    int_range_slider_disabled: tuple[int, int] = Field(default=(0, 3), ge=0, le=4, disabled=True)
    float_slider: float = Field(default=2.2, ge=1, le=3)
    float_text: float = 2.2
    float_text_locked: float = Field(default=2.2, disabled=True)
    float_range_slider: tuple[float, float] = Field(default=(0, 2.2), ge=0, le=3.5)
    checkbox: bool = True
    dropdown: FruitEnum = None
    dropdown_edge_case: FruitEnum = Field(
        title="FruitEnum with metadata",
        default=FruitEnum.apple,
        description="updated description",
    )
    dropdown_simple: str = Field(default="asd", enum=["asd", "asdf"])
    text: str = Field(default="adsf", description="a description about my string")
    text_short: constr(min_length=0, max_length=20) = "short text"
    text_area: constr(min_length=0, max_length=800) = Field(
        "long text " * 50, description="long text field"
    )
