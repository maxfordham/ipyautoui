"""
An example schema definition that demonstrates the current capability of the AutoUi class
"""

import typing as ty
import annotated_types
from enum import Enum
from pydantic import StringConstraints, Field, conint, confloat, ConfigDict
from ipyautoui.basemodel import BaseModel
from typing_extensions import Annotated


class TestEnum(Enum):
    a: str = "a"
    b: str = "b"


class NullAndRequired(BaseModel):
    # https://docs.pydantic.dev/latest/migration/#required-optional-and-nullable-fields
    f1: str = Field(description="Required, cannot be None")
    f2: ty.Optional[ty.Union[TestEnum, str]] = Field(
        "a", description="Not required, can be None, is 'a' by default"
    )
    f3: ty.Union[TestEnum, str] = Field(
        "a", description="Not required, cannot be None, is 'a' by default"
    )
    f4: ty.Optional[str] = Field(description="Required, can be None")  #
    f5: ty.Optional[str] = Field(
        None, description="Not required, can be None, is None by default"
    )  #
    f6: ty.Optional[str] = Field(
        "abc", description="Not required, can be None, is 'abc' by default"
    )  #
    # f7: ty.Any = Field() # Required, can be any type (including None) # NOT SUPPORTED IN IPYAUTOUI
    # f7: ty.Any = None  # Not required, can be any type (including None) # NOT SUPPORTED IN IPYAUTOUI
    # f7: str = None  # Not required, but if given must be a string. Defaults to None but cannot be set to None.  # NOT SUPPORTED IN IPYAUTOUI
    f7: str = Field(
        description="required, cannot be None, is 'abc' by default",
        json_schema_extra=dict(default="abc"),
    )
    f8: str = Field(max_length=5, examples=["ase", "qwe", "zxc"])
    # f11: TestEnum1
    # f12: TestEnum2
