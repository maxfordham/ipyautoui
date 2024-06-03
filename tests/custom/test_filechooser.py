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


def test_filechooser_set_value(tmp_path):
    # Make sure that setting a filename which does not exist works,
    # i.e. the filename is retained and the path is set to the parent directory.
    fc = FileChooser()
    fc.value = tmp_path / "does_not_exist.txt"
    assert fc.selected_filename == "does_not_exist.txt"
    assert fc.selected_path == str(tmp_path)

    # Try changing the value to a directory that exists.
    new_path = tmp_path / "new_directory"
    new_path.mkdir()
    fc.value = new_path
    assert fc.selected_filename == ""
    # Use samefile below so there is no need to worry about trailing slashes.
    assert (tmp_path / "new_directory").samefile(fc.selected_path)
