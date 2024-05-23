from pydantic import BaseModel, Field
from ipyautoui import AutoUi
from ipyautoui.custom.filechooser import FileChooser
import pathlib


def test_filechooser():
    class Test(BaseModel):
        path: pathlib.Path = Field(
            ".", json_schema_extra=dict(filter_pattern=["*_.py"])
        )  # note. filter_pattern ipyfilechooser kwarg passed on
        string: str = "test"

    ui = AutoUi(Test)

    assert isinstance(ui.di_widgets["path"], FileChooser)
    assert ui.di_widgets["path"].value == "."
    assert ui.di_widgets["path"].filter_pattern == ["*_.py"]
