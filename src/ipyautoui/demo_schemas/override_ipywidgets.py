from pydantic import Field
from ipyautoui.basemodel import BaseModel
import typing as ty

class OverrideIpywidgets(BaseModel):
    """sometimes it isn't possible to guess what widget to use based on type information.
    For example, the Combobox has the same inputs as a Dropdown. You can specify to use
    a specify widget using the `autoui` field.
    """

    combobox: str = Field(
        default="asd",
        json_schema_extra=dict(enum=["asd", "asdf"], autoui="ipywidgets.Combobox"),
    )
    combobox_mapped: str = Field(
        default="asd",
        json_schema_extra=dict(
            options={"ASD": "asd", "ASDF": "asdf"},
            autoui="ipyautoui.custom.combobox_mapped.ComboboxMapped",
        ),
    )
    toggle: bool = Field(
        default=True,
        title="Toggle Button",
        description="This is a toggle button, normally a checkbox is used for booleans.",
        json_schema_extra=dict(autoui="ipywidgets.ToggleButton"),
    )
    nullable_toggle_overide: ty.Optional[bool] = Field(
        default=None,
        title="Toggle Button",
        description="This is a toggle button, normally a checkbox is used for booleans.",
        json_schema_extra=dict(autoui="ipywidgets.ToggleButton"),
    )
    jsonable_dict: dict = Field(
        default={"a": [1,2,3]},
        title="Toggle Button",
        description="A simple user input string that is evaluated as a jsonable dict.",
        json_schema_extra=dict(autoui="ipyautoui.custom.JsonableDict"),
    )
