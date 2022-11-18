from pydantic import Field
from ipyautoui.basemodel import BaseModel


class OverrideIpywidgets(BaseModel):
    """sometimes it isn't possible to guess what widget to use based on type information.
    For example, the Combobox has the same inputs as a Dropdown. You can specify to use
    a specify widget using the `autoui` field.
    """

    combobox: str = Field(
        default="asd",
        enum=["asd", "asdf"],
        autoui="ipyautoui.autowidgets.Combobox",
    )
