from pydantic import Field
from ipyautoui.basemodel import BaseModel


class OverrideIpywidgets(BaseModel):
    combobox: str = Field(
        default="asd",
        enum=["asd", "asdf"],
        autoui="ipyautoui.autowidgets.Combobox",
    )
