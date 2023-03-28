from ipyautoui.demo import Demo
from ipyautoui.demo_schemas import CoreIpywidgets, Rule
from ipyautoui.autoipywidget import AutoObject
import inspect


class TestAutoObjectFormLayout:
    def test_show_raw(self):
        # check that that showraw gets added and removed on trait change
        d = Demo()
        assert d.pydantic_model == CoreIpywidgets
        assert d.python_file == inspect.getfile(CoreIpywidgets)


class TestFilters:
    def test_Rule(self):
        aui = AutoObject(schema=Rule)
        print("done")