import shutil
import pytest
import pandas as pd

# from src.ipyautoui.test_schema import TestSchema

# from ipyautoui.tests import test_display_widget_mapping
from .constants import DIR_TESTS, DIR_FILETYPES
from .example_objects import (
    fn_add,
    get_descriptions,
    ExampleSchema,
    ExampleDataFrameSchema,
    ExampleDataFrameSchema1,
    ExampleDataFrameSchema2,
)
from ipyautoui.custom.editgrid import AutoGrid, EditGrid
from ipyautoui.custom.save_buttonbar import ButtonBar
from ipyautoui.demo_schemas import EditableGrid
from ipyautoui.autoipywidget import AutoObject

# from ipyautoui.demo_schemas.editable_datagrid import DATAGRID_TEST_VALUE

DIR_TEST_DATA = DIR_TESTS / "test_data"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True)


def save():
    return "SAVE"


def revert():
    return "REVERT"


class TestButtonBar:
    def test_button_bar(self):
        def add():
            return "ADD"

        def edit():
            return "EDIT"

        def copy():
            return "COPY"

        def delete():
            return "DELETE"

        def backward():
            return "BACK"

        button_bar = ButtonBar(
            add=add,
            edit=edit,
            copy=copy,
            delete=delete,
            backward=backward,
        )
        assert button_bar.fn_add() == "ADD"

    # TODO: update EditGrid and associated tests
    # def test_base_form(self):
    #     baseform = BaseForm(schema=ExampleSchema, save=save, revert=revert)
    #     assert baseform.fn_save() == "SAVE"

    # def test_base_form_set_value(self):
    #     baseform = BaseForm(schema=ExampleSchema, save=save, revert=revert)
    #     di_eg_unit = {"text": "update"}
    #     baseform.value = di_eg_unit
    #     assert baseform.value == di_eg_unit


class TestAutoGridInitData:
    def test_empty_grid(self):

        # initiate empty grid
        grid = AutoGrid(schema=ExampleDataFrameSchema)
        assert grid._data["data"] == [
            {"key": 0, "String": "", "Floater": 0.0, "ipydguuid": 0}
        ]
        assert grid._data["schema"]["fields"] == [
            {"name": "key", "type": "integer"},
            {"name": "String", "type": "string"},
            {"name": "Floater", "type": "number"},
            {"name": "ipydguuid", "type": "integer"},
        ]

    def test_assign_default_at_root(self):
        # get default data from top-level schema defaults
        grid1 = AutoGrid(schema=ExampleDataFrameSchema1)
        assert grid1._data["data"] == [
            {"key": 0, "String": "test", "Floater": 1.5, "ipydguuid": 0}
        ]

    def test_assign_default_at_property_level(self):
        # get default data from schema property defaults
        grid2 = AutoGrid(schema=ExampleDataFrameSchema2)
        assert grid2._data["data"] == [
            {"key": 0, "String": "string", "Floater": 3.14, "ipydguuid": 0}
        ]

    def test_pass_data_as_kwarg(self):
        # get default data passed as kwarg, titles as column headers

        df = pd.DataFrame([{"String": "test2", "Floater": 2.2}])
        grid3 = AutoGrid(schema=ExampleDataFrameSchema2, data=df)
        assert grid3._data["data"] == [
            {"key": 0, "String": "test2", "Floater": 2.2, "ipydguuid": 0}
        ]

    def test_pass_data_as_kwarg_map_titles(self):
        # get default data passed as kwarg, keys as column headers. maps to titles
        df = pd.DataFrame([{"string": "test2", "floater": 2.2}])
        grid4 = AutoGrid(schema=ExampleDataFrameSchema2, data=df)
        assert grid4._data["data"] == [
            {"key": 0, "String": "test2", "Floater": 2.2, "ipydguuid": 0}
        ]
        print("done")


class TestEditGrid:
    def test_editgrid_change_data(self):
        grid = EditGrid(schema=EditableGrid)
        v = grid.value
        grid._save_add_to_grid()
        assert v != grid._value


class TestAutoEditGrid:
    def test_editgrid_change_data(self):
        grid = AutoObject(schema=EditableGrid)
        v = grid.value

        check = False

        def test_observe(on_change):
            check = True

        grid.di_widgets["__root__"].observe(test_observe, "_value")

        assert "_value" in grid.di_widgets["__root__"].traits()
        grid.di_widgets["__root__"]._save_add_to_grid()
        assert v != grid.di_widgets["__root__"].value
        assert check == True
        assert v != grid._value
