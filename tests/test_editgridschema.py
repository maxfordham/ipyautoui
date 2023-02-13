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
from ipyautoui.custom.autogrid import GridSchema
from pydantic import BaseModel, Field
import typing as ty

# from ipyautoui.demo_schemas.editable_datagrid import DATAGRID_TEST_VALUE

DIR_TEST_DATA = DIR_TESTS / "test_data"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True)


class TestGridSchema:
    def test_validate_editable_grid_schema(self):
        class TestProperties(BaseModel):
            string: str = Field(column_width=100)
            floater: float = Field(column_width=70, aui_sig_fig=3)

        class TestGridSchema(BaseModel):
            """no default"""

            __root__: ty.List[TestProperties] = Field(format="dataframe")

        model, schema = _init_model_schema(TestGridSchema)
        gridschema = GridSchema(schema)
        assert isinstance(gridschema, GridSchema)

        class TestGridSchemaFail(BaseModel):
            """no default"""

            __root__: ty.Dict[str, TestProperties] = Field(format="dataframe")

        with pytest.raises(ValueError):
            model, schema = _init_model_schema(TestGridSchemaFail)
            gridschema = GridSchema(schema)

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
        assert gridschema.get_default_dataframe().equals(
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
        assert gridschema.get_default_dataframe().equals(
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
        assert gridschema.get_default_dataframe().equals(
            pd.DataFrame(
                [{("a", "String"): "string", ("b", "Floater"): 1.5, ("b", "Inty"): 1}],
                columns=pd.MultiIndex.from_tuples(
                    [("a", "String"), ("b", "Floater"), ("b", "Inty")],
                    names=("section", "title"),
                ),
            )
        )

    def test_get_field_names_from_properties(self):
        class TestProperties(BaseModel):
            string: str = Field(column_width=100, section="a")
            floater: float = Field(1.5, column_width=70, aui_sig_fig=3, section="b")

        class TestGridSchema(BaseModel):
            """no default"""

            __root__: ty.List[TestProperties] = Field(
                [TestProperties(string="string").dict()],
                format="dataframe",
                datagrid_index_name=("section", "title"),
            )

        model, schema = _init_model_schema(TestGridSchema)
        gridschema = GridSchema(schema)
        assert gridschema.get_field_names_from_properties("title") == [
            "String",
            "Floater",
        ]
        assert gridschema.get_field_names_from_properties(
            "title", order=("floater",)
        ) == [
            "Floater",
        ]
        assert gridschema.get_field_names_from_properties(
            "title", order=("floater", "string")
        ) == [
            "Floater",
            "String",
        ]
        assert gridschema.get_field_names_from_properties(["section", "title"]) == [
            ("a", "String"),
            ("b", "Floater"),
        ]
        assert gridschema.get_field_names_from_properties(
            ["section", "title"], order=("floater", "string")
        ) == [
            ("b", "Floater"),
            ("a", "String"),
        ]

    def test_get_index(self):
        pass

    def test_coerce_data(self):
        class TestProperties(BaseModel):
            string: str = Field(column_width=100, section="a")
            floater: float = Field(1.5, column_width=70, aui_sig_fig=3, section="b")

        class TestGridSchema(BaseModel):
            """no default"""

            __root__: ty.List[TestProperties] = Field(
                [TestProperties(string="string").dict()],
                format="dataframe",
                datagrid_index_name=("section", "title"),
            )

        model, schema = _init_model_schema(TestGridSchema)
        gridschema = GridSchema(schema)
        data = gridschema.get_default_dataframe()
        df_check = pd.DataFrame(
            columns=gridschema.get_index(),
            data=[{("a", "String"): "string", ("b", "Floater"): 1.5}],
        )

        assert data.equals(df_check)
        assert list(data.columns) == list(gridschema.map_index_name.keys())
        # data = data.rename(columns=gridschema.map_index_name) # doesn't work
        # assert list(data.columns) == list(gridschema.map_index_name.values())
        df = pd.DataFrame.from_records(gridschema.default_data)
        data = gridschema.coerce_data(df)
        assert data.equals(df_check)

        print("done")
        # assert data == pd.DataFrame.
