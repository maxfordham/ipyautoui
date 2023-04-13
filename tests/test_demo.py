import inspect
from pathlib import PosixPath
from ipyautoui.demo import Demo
from ipyautoui.demo_schemas import CoreIpywidgets


class TestAutoObjectFormLayout:
    def test_show_raw(self):
        # check that that showraw gets added and removed on trait change
        d = Demo()
        assert d.pydantic_model == CoreIpywidgets
        assert d.python_file == PosixPath(inspect.getfile(CoreIpywidgets))
