from pydantic import BaseModel, Field, RootModel
import typing as ty
import pandas as pd

from .constants import DIR_TESTS
from ipyautoui.custom.editgrid import EditGrid
from ipyautoui.custom.buttonbars import CrudButtonBar
from ipyautoui.demo_schemas.editable_datagrid import EditableGrid, DataFrameCols
from ipyautoui import AutoUi


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
            fn_add=add,
            fn_edit=edit,
            fn_copy=copy,
            fn_delete=delete,
            fn_backward=backward,
        )
        assert button_bar.fn_add() == "ADD"


class TestEditGrid:
    def test_editgrid_change_data(self):
        grid = EditGrid(schema=EditableGrid)
        v = grid.value
        grid._save_add_to_grid()
        assert v != grid._value

    def test_editgrid_set_data(self):
        pass # WIP


    def test_editgrid_multiindex_change_data(self):
        class TestProperties(BaseModel):
            string: str = Field(json_schema_extra=dict(column_width=100, section="a"))
            floater: float = Field(
                1.5,
                json_schema_extra=dict(
                    column_width=70, global_decimal_places=3, section="b"
                ),
            )
            inty: int = Field(1, json_schema_extra=dict(section="b"))

        class TestGridSchema(RootModel):
            """no default"""

            root: ty.List[TestProperties] = Field(
                [TestProperties(string="string").model_dump()],
                json_schema_extra=dict(
                    format="dataframe", datagrid_index_name=("section", "title")
                ),
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

    def test_editgrid_duplicate_transposed(self):
        grid = EditGrid(schema=EditableGrid)
        grid.grid.transposed = True
        grid.grid.selections = [{"r1": 0, "r2": 4, "c1": 0, "c2": 0}]
        grid._copy()
        # assert grid.grid.selections == []
        df = grid.grid.get_visible_data()
        assert isinstance(df, pd.DataFrame)
        print("done")

    def test_editgrid_edit_transposed(self):
        grid = EditGrid(schema=EditableGrid)
        grid.grid.transposed = True
        grid.grid.selections = [{"r1": 0, "r2": 4, "c1": 0, "c2": 0}]
        grid._copy()
        grid.grid.selections = [{"r1": 0, "r2": 4, "c1": 1, "c2": 1}]
        grid._copy()
        grid.grid.selections = [{"r1": 0, "r2": 4, "c1": 1, "c2": 1}]
        grid.ui_edit.value = DataFrameCols(string="mystring").model_dump(mode="json")
        grid._save_edit_to_grid()
        # assert grid.grid.selections == []

        grid.grid.selections = [{"r1": 0, "r2": 4, "c1": 21, "c2": 2}]
        grid.ui_edit.value = DataFrameCols(integer=0, string="mystring-1").model_dump(
            mode="json"
        )
        grid._save_edit_to_grid()
        df = grid.grid.get_visible_data()
        assert isinstance(df, pd.DataFrame)
        print("done")

    def test_update_from_schema(self):
        editgrid = EditGrid()

        class DataFrameCols(BaseModel):
            string: str = Field(
                "string", json_schema_extra=dict(column_width=400, section="a")
            )

        class TestDataFrame(RootModel):
            """a description of TestDataFrame"""

            root: ty.List[DataFrameCols] = Field(
                json_schema_extra=dict(
                    format="dataframe", datagrid_index_name=("section", "title")
                ),
            )

        value = [{"string": "Test"}] * 10
        editgrid.update_from_schema(TestDataFrame, value=[{"string": "Test"}] * 10)
        import jsonref

        json_schema = jsonref.replace_refs(
            TestDataFrame.model_json_schema(), merge_props=True
        )
        import copy

        # Make deep copies to avoid modifying the original dictionaries
        schema_copy = copy.deepcopy(editgrid.schema)
        json_schema_copy = copy.deepcopy(json_schema)

        # Remove the $defs key from both copies if it exists
        schema_copy.pop("$defs", None)
        json_schema_copy.pop("$defs", None)

        # Now compare the modified copies
        assert schema_copy == json_schema_copy
        assert list(editgrid.value) == value


def test_show_hide_nullable():
    class TestProperties(BaseModel):
        string: str
        nullable_string: ty.Optional[str] = None
        floater: float = 1.5
        inty: int = 1

    class TestGridSchema(RootModel):
        """no default"""

        root: ty.List[TestProperties] = Field(
            [TestProperties(string="string").model_dump()],
        )

    egrid = EditGrid(
        schema=TestGridSchema,
        value=[{"string": "test2", "nullable_string": None, "floater": 2.2, "inty": 1}],
    )
    assert egrid.ui_edit.bn_shownull.layout.display == ""


def test_selected_cells():
    class TestProperties(BaseModel):
        string: str
        # nullable_string: ty.Optional[str] = None
        floater: float = 1.5
        inty: int = 1

    class TestGridSchema(RootModel):
        """no default"""

        root: ty.List[TestProperties] = Field(
            [TestProperties(string="string").model_dump()],
        )

    egrid = EditGrid(
        schema=TestGridSchema,
        value=[{"string": "test2", "floater": 2.2, "inty": 1}]
        * 4,  # "nullable_string":None,
    )
    egrid.grid.select(1, 1)
    egrid.grid.transposed = True
    index = egrid.grid.selected_indexes[0]
    assert index == 1

    # assert egrid.grid.selected_indexes == [1]  # TODO: check if we should be resetting on transpose
    egrid.ui_edit.value = egrid.ui_edit.value | {"string": "test", "inty": 0}
    egrid._save_edit_to_grid()
    assert egrid.value[index]["inty"] == 0
    print("done")


class TestAutoEditGrid:
    def test_editgrid_change_data(self):
        grid = AutoUi(schema=EditableGrid)
        v = grid.value

        assert "_value" in grid.traits()
        assert v == grid.value
        grid._save_add_to_grid()
        assert v != grid.value
        assert v != grid._value
