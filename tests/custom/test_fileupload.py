from ipyautoui.custom.fileupload import File, FileUi, FileUploadToDir
import pathlib

FDIR_TEST = pathlib.Path(__file__).parents[1] / 'testdata'

class TestFileUi:
    def test_file_ui(self):
        f = File(name="test_savebuttonbar.py")
        fui = FileUi(f)
        assert fui.show_caption == True
        assert fui.caption.layout.display == None

        fui.show_caption = False
        assert fui.show_caption == False
        assert fui.caption.layout.display == "None"

        fui.show_caption = True
        assert fui.caption.layout.display == ""

# class TestFileUploadToDir: