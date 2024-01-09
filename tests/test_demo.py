import inspect
from pathlib import PosixPath
from ipyautoui.demo import Demo, DemoReel
from ipyautoui.demo_schemas import CoreIpywidgets, OverrideIpywidgets


class TestDemo:
    def test_demo(self):
        # check that that showraw gets added and removed on trait change
        d = Demo()
        assert d.pydantic_model == CoreIpywidgets
        assert d.python_file == PosixPath(inspect.getfile(CoreIpywidgets))
        for k, wi in d.autoui.di_widgets.items():
            nm = str(wi.__class__)
            assert "WidgetCallerError" not in nm
            
    def test_change_pydantic_model(self):
        # check that that showraw gets added and removed on trait change
        d = Demo()
        assert d.pydantic_model == CoreIpywidgets
        assert d.python_file == PosixPath(inspect.getfile(CoreIpywidgets))
        d.pydantic_model = OverrideIpywidgets
        assert d.pydantic_model == OverrideIpywidgets
        assert d.python_file == PosixPath(inspect.getfile(OverrideIpywidgets))


    def test_demoreel(self):
        # check that that showraw gets added and removed on trait change
        dr = DemoReel()
        print("done")
