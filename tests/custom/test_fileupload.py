from ipyautoui.custom.fileupload import FilesUploadToDir
import pathlib

FDIR_TEST = pathlib.Path(__file__).parents[1] / "testdata"


class TestFileUi:
    def test_file_ui(self):
        f = FilesUploadToDir(["test_buttonbars.py"])
        assert f.value == ["test_buttonbars.py"]
