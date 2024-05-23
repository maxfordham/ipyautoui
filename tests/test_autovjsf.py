from ipyautoui.autovjsf import AutoVjsf, Vjsf
from ipyautoui.demo_schemas import CoreIpywidgets
import pathlib


def test_Vjsf():
    schema = CoreIpywidgets.model_json_schema()
    ui = Vjsf(schema=schema)
    assert ui.schema == CoreIpywidgets.model_json_schema()

    # assert ui.value == CoreIpywidgets(int_text_req=0, int_text_nullable=None).model_dump()
    # ^ don't think this works cos JS needs to run...


def test_AutoVjsf():

    ui = AutoVjsf(
        schema=CoreIpywidgets,
    )
    assert ui.value == {}
    # assert ui.autowidget.value == CoreIpywidgets(int_text_req=0, int_text_nullable=None).model_dump()
    # ^ don't think this works cos JS needs to run...
