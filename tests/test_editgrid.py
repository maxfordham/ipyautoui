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
from ipyautoui.custom.editgrid import GridSchema, AutoObjectFiltered
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


class TestGridSchema:
    def test_empty_default_data(self):
        class TestProperties(BaseModel):
            string: str = Field(column_width=100)
            floater: float = Field(column_width=70, aui_sig_fig=3)

        class TestGridSchema(BaseModel):
            """no default"""

            __root__: ty.List[TestProperties] = Field(format="dataframe")

        model, schema = _init_model_schema(TestGridSchema)
        gridschema = GridSchema(schema)

        assert gridschema.index_name == "title"
        assert (gridschema.index == pd.Index(["String", "Floater"], name="title")).all()
        assert gridschema.default_data == []
        assert gridschema.default_row == {"string": None, "floater": None}
        assert gridschema.default_dataframe.equals(
            pd.DataFrame(columns=pd.Index(["String", "Floater"], name="title"))
        )

    def test_partial_row_default_data(self):
        class TestProperties(BaseModel):
            string: str = Field(column_width=100)
            floater: float = Field(1.5, column_width=70, aui_sig_fig=3)

        class TestGridSchema(BaseModel):
            """no default"""

            __root__: ty.List[TestProperties] = Field(
                [TestProperties(string="string").dict()], format="dataframe"
            )

        model, schema = _init_model_schema(TestGridSchema)
        gridschema = GridSchema(schema)
        assert gridschema.is_multiindex == False
        assert gridschema.default_data == [{"string": "string", "floater": 1.5}]
        assert gridschema.default_row == {"string": None, "floater": 1.5}
        assert gridschema.default_dataframe.equals(
            pd.DataFrame(
                [{"String": "string", "Floater": 1.5}],
                columns=pd.Index(["String", "Floater"], name="title"),
            )
        )

    def test_multiindex(self):
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

        model, schema = _init_model_schema(TestGridSchema)
        gridschema = GridSchema(schema)

        assert gridschema.is_multiindex == True
        assert gridschema.index.equals(
            pd.MultiIndex.from_tuples(
                [("a", "String"), ("b", "Floater"), ("b", "Inty")],
                names=("section", "title"),
            )
        )
        assert gridschema.default_data == [
            {"string": "string", "floater": 1.5, "inty": 1}
        ]
        assert gridschema.default_row == {"floater": 1.5, "inty": 1, "string": None}
        # TODO: this doesn't make that much sense ans string=None is not allowed...
        assert gridschema.default_dataframe.equals(
            pd.DataFrame(
                [{("a", "String"): "string", ("b", "Floater"): 1.5, ("b", "Inty"): 1}],
                columns=pd.MultiIndex.from_tuples(
                    [("a", "String"), ("b", "Floater"), ("b", "Inty")],
                    names=("section", "title"),
                ),
            )
        )


class TestAutoGridInitData:
    def test_empty_grid(self):
        class Cols(BaseModel):
            string: str = Field(aui_column_width=100)
            floater: float = Field(aui_column_width=70, aui_sig_fig=3)

        class DataFrameSchema(BaseModel):
            """no default"""

            __root__: ty.List[Cols] = Field(format="dataframe")

        # initiate empty grid
        grid = AutoGrid(schema=DataFrameSchema)
        assert grid._data["data"] == []
        assert grid._data["schema"]["fields"] == [
            {"name": "index", "type": "string"},  # NOTE: unable to detect type
            {"name": "String", "type": "string"},
            {"name": "Floater", "type": "string"},  # NOTE: unable to detect type
            {"name": "ipydguuid", "type": "integer"},
        ]

    def test_assign_default_at_root(self):
        # get default data from top-level schema defaults

        class Cols(BaseModel):
            string: str = Field("string", aui_column_width=100)
            floater: float = Field(3.14, aui_column_width=70, aui_sig_fig=3)

        class DataFrameSchema(BaseModel):
            """default."""

            __root__: ty.List[Cols] = Field(
                [Cols(string="test", floater=1.5).dict()], format="dataframe"
            )

        grid = AutoGrid(schema=DataFrameSchema)
        assert grid._data["data"] == [
            {"index": 0, "String": "test", "Floater": 1.5, "ipydguuid": 0}
        ]

    def test_pass_data_as_kwarg(self):
        # get default data passed as kwarg, titles as column headers
        class Cols(BaseModel):
            string: str = Field("string", aui_column_width=100)
            floater: float = Field(3.14, aui_column_width=70, aui_sig_fig=3)

        class DataFrameSchema(BaseModel):
            """no default. but properties have default"""

            __root__: ty.List[Cols] = Field(format="dataframe")

        df = pd.DataFrame([{"String": "test2", "Floater": 2.2}])
        grid3 = AutoGrid(schema=DataFrameSchema, data=df)
        assert grid3._data["data"] == [
            {"index": 0, "String": "test2", "Floater": 2.2, "ipydguuid": 0}
        ]

    def test_pass_data_as_kwarg_map_titles(self):
        # get default data passed as kwarg, keys as column headers. maps to titles

        class Cols(BaseModel):
            string: str = Field("string", aui_column_width=100)
            floater: float = Field(3.14, aui_column_width=70, aui_sig_fig=3)

        class DataFrameSchema(BaseModel):
            """no default. but properties have default"""

            __root__: ty.List[Cols] = Field(format="dataframe")

        df = pd.DataFrame([{"string": "test2", "floater": 2.2}])
        grid4 = AutoGrid(schema=DataFrameSchema, data=df)
        assert grid4._data["data"] == [
            {"index": 0, "String": "test2", "Floater": 2.2, "ipydguuid": 0}
        ]
        print("done")

    def test_reset_multiindex_data_with_init_data(self):
        # get default data passed as kwarg, keys as column headers. maps to titles

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

        df = pd.DataFrame([{"string": "test2", "floater": 2.2, "inty": 1}])
        gr = AutoGrid(schema=TestGridSchema, data=df)

        assert gr._data["data"] == [
            {
                ("index", ""): 0,
                ("a", "String"): "test2",
                ("b", "Floater"): 2.2,
                ("b", "Inty"): 1,
                ("ipydguuid", ""): 0,
            }
        ]

        df1 = pd.DataFrame([{"string": "test2", "floater": 2.2, "inty": 1}] * 2)
        gr.data = gr._init_data(df1)

        assert gr._data["data"] == [
            {
                ("a", "String"): "test2",
                ("b", "Floater"): 2.2,
                ("b", "Inty"): 1,
                ("ipydguuid", ""): 0,
                ("index", ""): 0,
            },
            {
                ("a", "String"): "test2",
                ("b", "Floater"): 2.2,
                ("b", "Inty"): 1,
                ("ipydguuid", ""): 1,
                ("index", ""): 1,
            },
        ]

        gr.transposed = True
        df = gr._init_data(
            pd.DataFrame([{"string": "test2", "floater": 2.2, "inty": 1}])
        )
        print("done")

    @pytest.mark.parametrize("transposed", [True, False])
    def test_order_index(self, transposed: bool):
        class Cols(BaseModel):
            string: str = Field(aui_column_width=100)
            floater: float = Field(aui_column_width=70, aui_sig_fig=3)

        class DataFrameSchema(BaseModel):
            """no default"""

            __root__: ty.List[Cols] = Field(format="dataframe")

        order_override = ("floater", "string")
        # Test without data passed
        grid_without_data = AutoGrid(
            schema=DataFrameSchema, 
            transposed=transposed, 
            order_override=order_override
        )
        # Test with data passed
        grid_with_data = AutoGrid(
            schema=DataFrameSchema, 
            data=pd.DataFrame([Cols(string="test", floater=2.5).dict()]),
            transposed=transposed, 
            order_override=order_override
        )
        if transposed is True:
            assert tuple(grid_without_data.data.index) == tuple([
                grid_without_data.map_name_index.get(name) for name in order_override
            ])
            assert tuple(grid_with_data.data.index) == tuple([
                grid_with_data.map_name_index.get(name) for name in order_override
            ])
        else:
            assert tuple(grid_without_data.data.columns) == tuple([
                grid_without_data.map_name_index.get(name) for name in order_override
            ])
            assert tuple(grid_with_data.data.columns) == tuple([
                grid_with_data.map_name_index.get(name) for name in order_override
            ])

    @pytest.mark.parametrize("transposed", [True, False])
    def test_order_multi_index(self, transposed: bool):
        class Cols(BaseModel):
            string: str = Field(aui_column_width=100, title="String", section="a")
            floater: float = Field(
                aui_column_width=70, aui_sig_fig=3, title="Floater", section="a"
            )

        class DataFrameSchema(BaseModel):
            """no default"""

            __root__: ty.List[Cols] = Field(
                format="dataframe",
                datagrid_index_name=("section", "title"),
            )

        order_override = ("floater", "string")
        # Test without data passed
        grid_without_data = AutoGrid(
            schema=DataFrameSchema, 
            transposed=transposed, 
            order_override=order_override
        )
        # Test with data passed
        grid_with_data = AutoGrid(
            schema=DataFrameSchema, 
            data=pd.DataFrame([Cols(string="test", floater=2.5).dict()]),
            transposed=transposed, 
            order_override=order_override
        )
        if transposed is True:
            assert tuple(grid_without_data.data.index) == tuple([
                grid_without_data.map_name_index.get(name) for name in order_override
            ])
            assert tuple(grid_with_data.data.index) == tuple([
                grid_with_data.map_name_index.get(name) for name in order_override
            ])
        else:
            assert tuple(grid_without_data.data.columns) == tuple([
                grid_without_data.map_name_index.get(name) for name in order_override
            ])
            assert tuple(grid_with_data.data.columns) == tuple([
                grid_with_data.map_name_index.get(name) for name in order_override
            ])


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
            {"string": "string", "floater": 1.5, "inty": 1},
            {"string": "", "floater": 1.5, "inty": 1},
        )

        # copy
        egrid.grid.select(row1=1, column1=1, row2=1, column2=1, clear_mode="all")
        egrid._copy()
        assert egrid.value == (
            {"string": "string", "floater": 1.5, "inty": 1},
            {"string": "", "floater": 1.5, "inty": 1},
            {"string": "", "floater": 1.5, "inty": 1},
        )

        # delete
        egrid.grid.select(row1=1, column1=2, row2=1, column2=2, clear_mode="all")
        egrid._delete_selected()
        assert egrid.value == (
            {"string": "string", "floater": 1.5, "inty": 1},
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
