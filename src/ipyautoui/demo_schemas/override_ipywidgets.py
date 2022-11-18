from pydantic import Field
from ipyautoui.basemodel import BaseModel


class OverrideIpywidgets(BaseModel):
    """when generating the widget to match parameter defined in the pydantic model / jsonschema,
    AutoUi looks at thinks like: type, options, min / max etc. to guess what widget to use.
    Some widgets have the same characteristics, so we need to specify explicitly which to use.
    This can be done by adding a `autoui` property to the Field as shown below.
    """

    combobox: str = Field(
        default="asd",
        enum=["asd", "asdf"],
        autoui="ipyautoui.autowidgets.Combobox",
    )
