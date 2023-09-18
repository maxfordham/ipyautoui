import inspect
from pathlib import PosixPath
from ipyautoui.demo_schemas import (
    CoreIpywidgets,
    ArrayObjectDataframe,
    OverrideIpywidgets,
)
from ipyautoui import AutoUi


def assert_no_error_widget_in_autoui(autoui):
    for k, wi in autoui.di_widgets.items():
        nm = str(wi.__class__)
        try:
            assert "WidgetCallerError" not in nm
        except Exception as e:
            e_title = autoui.schema.title
            e_nm = nm
            e_key = k
            raise e


def test_CoreIpywidgets():
    autoui = AutoUi(CoreIpywidgets)
    assert_no_error_widget_in_autoui(autoui)


def test_ArrayObjectDataframe():
    autoui = AutoUi(ArrayObjectDataframe, fail_on_error=True)
    assert_no_error_widget_in_autoui(autoui)


def test_OverrideIpywidgets():
    autoui = AutoUi(OverrideIpywidgets)
    assert_no_error_widget_in_autoui(autoui)
