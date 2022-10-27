import shutil
import pytest

# from src.ipyautoui.test_schema import TestSchema

# from ipyautoui.tests import test_display_widget_mapping
from .constants import DIR_TESTS, DIR_FILETYPES
from .example_objects import (
    fn_add,
    get_descriptions,
    ExampleSchema,
    ExampleDataFrameSchema,
)
from ipyautoui.custom import (
    Array,
    Dictionary,
    MultiSelectSearch,
    SaveButtonBar,
    LoadProject,
)
from ipyautoui.custom.modelrun import RunName
from ipyautoui.custom.editgrid import BaseForm, GridWrapper, EditGrid, ButtonBar
from ipyautoui.automapschema import attach_schema_refs


DIR_TEST_DATA = DIR_TESTS / "test_data"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True)
shutil.rmtree(
    DIR_TEST_DATA
)  #  remove previous data. this allows tests to check if files exist.


class TestCustom:
    def test_iterables_array(self):
        di_arr = {
            "items": [fn_add()],
            "fn_add": fn_add,
            "maxlen": 10,
            "show_hash": "index",
            "toggle": True,
            "title": "Array",
            "add_remove_controls": "append_only",
            "orient_rows": False,
        }
        arr = Array(**di_arr)

    def test_iterables_dict(self):
        di_arr = {
            "items": {"key": fn_add()},
            "fn_add": fn_add,
            "maxlen": 10,
            "show_hash": None,
            "toggle": True,
            "title": "Array",
            "add_remove_controls": "append_only",
            "orient_rows": True,
        }
        arr = Dictionary(**di_arr)

    def test_model_run(self):
        run = RunName(value="03-lean-description", index=3)
        run.value = "06-green-thingymabob"

    def test_multiselect_search(self):
        descriptions = get_descriptions()
        m = MultiSelectSearch(options=descriptions)

    def test_save_button_bar(self):
        save_button_bar = SaveButtonBar()

    def test_load_project(self):
        load_project = LoadProject()
