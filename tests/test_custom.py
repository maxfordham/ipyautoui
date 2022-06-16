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

dataframe_schema = attach_schema_refs(ExampleDataFrameSchema.schema())["properties"][
    "dataframe"
]


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

    # def test_grid(self): # TODO: add Grid tests once fixed
    #     gr = Grid()

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

    def test_button_bar(self):
        def add():
            print("ADD")

        def edit():
            print("EDIT")

        def copy():
            print("EDIT")

        def delete():
            print("DELETE")

        def backward():
            print("BACK")

        button_bar = ButtonBar(
            add=add, edit=edit, copy=copy, delete=delete, backward=backward,
        )

    # TODO: update EditGrid and associated tests
    def test_base_form(self):
        def save():
            print("SAVE")

        def revert():
            print("REVERT")

        baseform = BaseForm(schema=ExampleSchema, save=save, revert=revert)

    def test_base_form_set_value(self):
        def save():
            print("SAVE")

        def revert():
            print("REVERT")

        base_form = BaseForm(schema=ExampleSchema, save=save, revert=revert)
        di_eg_unit = {"text": "update"}
        base_form.value = di_eg_unit

    def test_grid_wrapper(self):

        grid = GridWrapper(schema=dataframe_schema,)

    def test_editgrid(self):
        grid = EditGrid(schema=dataframe_schema,)

