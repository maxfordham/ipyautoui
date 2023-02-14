import shutil
import pytest
import pandas as pd

# from src.ipyautoui.test_schema import TestSchema

# from ipyautoui.tests import test_display_widget_mapping
from .constants import DIR_TESTS, DIR_FILETYPES
from ipyautoui.custom.editgrid import AutoGrid, EditGrid
from ipyautoui.custom.buttonbars import CrudButtonBar
from ipyautoui.demo_schemas import EditableGrid
from ipyautoui.autoipywidget import AutoObject
from ipyautoui.automapschema import _init_model_schema
from ipyautoui.custom.editgrid import AutoObjectFiltered
from pydantic import BaseModel, Field
import typing as ty

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

        button_bar = CrudButtonBar(
            add=add,
            edit=edit,
            copy=copy,
            delete=delete,
            backward=backward,
        )
        assert button_bar.fn_add() == "ADD"


class TestEditGrid:
    def test_editgrid_change_data(self):
        grid = EditGrid(schema=EditableGrid)
        v = grid.value
        grid._save_add_to_grid()
        assert v != grid._value

    def test_editgrid_multiindex_change_data(self):
        class TestProperties(BaseModel):
            string: str = Field(column_width=100, section="a")
            floater: float = Field(1.5, column_width=70, aui_sig_fig=3, section="b")
            inty: int = Field(1, section="b")

        class TestGridSchema(BaseModel):
            """no default"""

            __root__: ty.List[TestProperties] = Field(
                [TestProperties(string="string").dict()],
                format="dataframe",
                datagrid_index_name=("section", "title"),
            )

        # df = pd.DataFrame([{"string": "test2", "floater": 2.2, "inty": 1}])
        egrid = EditGrid(
            schema=TestGridSchema,
            value=[{"string": "test2", "floater": 2.2, "inty": 1}],
        )
        egrid.transposed = True

        # add
        egrid._save_add_to_grid()
        assert egrid.value == (
            {"string": "test2", "floater": 2.2, "inty": 1},
            {"string": "", "floater": 1.5, "inty": 1},
        )

        # copy
        egrid.grid.select(row1=1, column1=1, row2=1, column2=1, clear_mode="all")
        egrid._copy()
        assert egrid.value == (
            {"string": "test2", "floater": 2.2, "inty": 1},
            {"string": "", "floater": 1.5, "inty": 1},
            {"string": "", "floater": 1.5, "inty": 1},
        )

        # delete
        egrid.grid.select(row1=1, column1=2, row2=1, column2=2, clear_mode="all")
        egrid._delete_selected()
        assert egrid.value == (
            {"string": "test2", "floater": 2.2, "inty": 1},
            {"string": "", "floater": 1.5, "inty": 1},
        )

        # edit
        # egrid.grid.select(row1=1, column1=1, row2=1, column2=1, clear_mode="all")
        # egrid.ui_edit.value = {"string": "test", "floater": 1.5, "inty": 1}
        # egrid._save_edit_to_grid()
        # assert egrid.value == (
        #     {"string": "string", "floater": 1.5, "inty": 1},
        #     {"string": "test", "floater": 1.5, "inty": 1},
        # )
        # print("done")

    def test_editgrid_with_auto_object_filtered(self):
        """Checking that instantiating EditGrid with AutoObjectFiltered."""

        class TestProperties(BaseModel):
            string: str = Field(column_width=100, section="a")
            floater: float = Field(1.5, column_width=70, aui_sig_fig=3, section="b")
            inty: int = Field(1, section="b")

        class TestGridSchema(BaseModel):
            """no default"""

            __root__: ty.List[TestProperties] = Field(
                [TestProperties(string="string").dict()],
                format="dataframe",
                datagrid_index_name=("section", "title"),
            )

        editgrid = EditGrid(
            schema=TestGridSchema,
            ui_add=AutoObjectFiltered,
            ui_edit=AutoObjectFiltered,
            warn_on_delete=True,
        )
        editgrid.observe(lambda c: print("_value changed"), "_value")
        editgrid.transposed = True

        # TODO: Check that transform updates order of AutoObjects
        # transform = [
        #     {
        #         'type': 'filter',
        #         'columnIndex': 1,
        #         'operator': 'in',
        #         'value': ['String', 'Floater']
        #     }
        # ]
        # editgrid.grid.transform(transform)
        # assert editgrid.ui_add.order == ['string', 'floater']
        # assert editgrid.ui_edit.order == ['string', 'floater']


class TestAutoEditGrid:
    @pytest.mark.skip(
        reason=(
            "not sure if this will work - does it need javascript / backbonejs"
            " traitlets stuff to be running? will they not running without the notebook"
            " session?"
        )
    )
    def test_editgrid_change_data(self):
        grid = AutoObject(schema=EditableGrid)
        v = grid.value.copy()

        check = False

        def test_observe(on_change):
            check = True

        grid.di_widgets["__root__"].observe(test_observe, "_value")

        assert "_value" in grid.di_widgets["__root__"].traits()
        grid.di_widgets["__root__"]._save_add_to_grid()
        assert v != grid.di_widgets["__root__"].value
        assert v != grid._value
        assert check == True
