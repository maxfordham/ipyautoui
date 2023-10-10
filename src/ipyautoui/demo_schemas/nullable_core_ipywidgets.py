import typing as ty
from enum import Enum
from pydantic import StringConstraints, Field
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


class NullableCoreIpywidgets(BaseModel):
    """This is a test UI form to demonstrate how pydantic class can be used to generate an ipywidget input form.
    Only simple datatypes used (i.e. not lists/arrays or objects).
    All set to be nullable.
    """

    int_slider_req: Annotated[int, Field(ge=1, le=3)] = None
    int_slider_nullable: Annotated[int, Field(ge=1, le=3)] = None
    int_slider: Annotated[int, Field(ge=1, le=3)] = None
    int_text: int = None
    int_range_slider: tuple[int, int] = Field(default=None, ge=0, le=4)
    float_slider: float = Field(default=None, ge=1, le=3)
    float_text: float = None
    float_text_locked: float = Field(
        default=None, json_schema_extra=dict(disabled=True)
    )
    float_range_slider: tuple[float, float] = Field(default=None, ge=0, le=3.5)
    checkbox: bool = None
    dropdown: FruitEnum = None
    dropdown_edge_case: FruitEnum = Field(
        title="FruitEnum with metadata",
        default=None,
        description="updated description",
    )
    dropdown_simple: str = Field(default=None, enum=["asd", "asdf"])
    text: str = Field(default=None, description="a description about my string")
    text_short: Annotated[str, StringConstraints(min_length=0, max_length=20)] = None
    text_area: Annotated[str, StringConstraints(min_length=0, max_length=800)] = Field(
        None, description="long text field"
    )
