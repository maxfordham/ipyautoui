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
from ipyautoui.custom.editgrid import BaseForm, GridWrapper, EditGrid, ButtonBar


DIR_TEST_DATA = DIR_TESTS / "test_data"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True)


def save():
    return "SAVE"


def revert():
    return "REVERT"


class TestEditGrid:
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
    def test_base_form(self):
        baseform = BaseForm(schema=ExampleSchema, save=save, revert=revert)
        assert baseform.fn_save() == "SAVE"

    def test_base_form_set_value(self):
        baseform = BaseForm(schema=ExampleSchema, save=save, revert=revert)
        di_eg_unit = {"text": "update"}
        baseform.value = di_eg_unit
        assert baseform.value == di_eg_unit

    def test_grid_wrapper(self):

        grid = GridWrapper(
            schema=ExampleDataFrameSchema,
        )
        print("done")

    def test_editgrid(self):
        grid = EditGrid(
            schema=dataframe_schema,
        )
