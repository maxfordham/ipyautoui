import inspect
from pathlib import PosixPath
from ipyautoui.demo_schemas import (
    CoreIpywidgets,
    ArrayObjectDataframe,
    OverrideIpywidgets,
    EditableGrid,
    ScheduleRuleSet,
    RootEnum
    # ScheduleRuleSet,
)
from ipyautoui import AutoUi

# NOTE: refer also to test_automapschema.py to ensure mappings are correct
def assert_no_error_widget_in_autoui(autoui):
    for k, wi in autoui.autowidget.di_widgets.items():
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


def test_ScheduleRuleSet():

    autoui = AutoUi(ScheduleRuleSet)
    assert_no_error_widget_in_autoui(autoui)
    
def test_EditableGrid():
    
    autoui = AutoUi(EditableGrid)
    assert "EditGrid" in str(autoui.autowidget)
    
def test_RootEnum():
    from ipyautoui.demo_schemas import RootEnum
    
    autoui = AutoUi(RootEnum)
    assert "SelectMultiple" in str(autoui.autowidget)
    # autoui.add_row()
    # assert "SelectMultiple" in str(autoui.li_widgets[0])