import pytest
import pandas as pd
from pydantic import BaseModel, Field, RootModel
import typing as ty

from ipyautoui.custom.autogrid import AutoGrid, GridSchema
from ipyautoui.automapschema import _init_model_schema

from .constants import DIR_TESTS

# from ipyautoui.demo_schemas.editable_datagrid import DATAGRID_TEST_VALUE

DIR_TEST_DATA = DIR_TESTS / "test_data"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True)


class TestGridSchema:
    def test_validate_editable_grid_schema(self):
        class TestProperties(BaseModel):
            string: str = Field(json_schema_extra=dict(column_width=100))
            floater: float = Field(json_schema_extra=dict(column_width=70, global_decimal_places=3))

        class TestGridSchema(RootModel):
            """no default"""

            root: ty.List[TestProperties] = Field(json_schema_extra=dict(format="dataframe"))

        model, schema = _init_model_schema(TestGridSchema)
        gridschema = GridSchema(schema)
        assert isinstance(gridschema, GridSchema)

        class TestGridSchemaFail(RootModel):
            """no default"""

            root: ty.Dict[str, TestProperties] = Field(json_schema_extra=dict(format="dataframe"))

        with pytest.raises(ValueError):
            model, schema = _init_model_schema(TestGridSchemaFail)
            gridschema = GridSchema(schema)

    def test_empty_default_data(self):
        class TestProperties(BaseModel):
            string: str = Field(json_schema_extra=dict(column_width=100))
            floater: float = Field(json_schema_extra=dict(column_width=70, global_decimal_places=3))

        class TestGridSchema(RootModel):
            """no default"""

            root: ty.List[TestProperties] = Field(json_schema_extra=dict(format="dataframe"))

        model, schema = _init_model_schema(TestGridSchema)
        gridschema = GridSchema(schema)

        assert gridschema.index_name == "title"
        assert (gridschema.index == pd.Index(["String", "Floater"], name="title")).all()
        assert gridschema._get_default_data() == []
        assert gridschema.default_row == {"string": None, "floater": None}
        assert gridschema.get_default_dataframe().equals(
            pd.DataFrame(columns=pd.Index(["String", "Floater"], name="title"))
        )

    def test_partial_row_default_data(self):
        class TestProperties(BaseModel):
            string: str = Field(json_schema_extra=dict(column_width=100))
            floater: float = Field(1.5, json_schema_extra=dict(column_width=70, global_decimal_places=3))

        class TestGridSchema(RootModel):
            """no default"""

            root: ty.List[TestProperties] = Field(
                [TestProperties(string="string").model_dump()], json_schema_extra=dict(format="dataframe")
            )

        model, schema = _init_model_schema(TestGridSchema)
        gridschema = GridSchema(schema)
        assert gridschema.is_multiindex == False
        assert gridschema._get_default_data() == [{"string": "string", "floater": 1.5}]
        assert gridschema.default_row == {"string": None, "floater": 1.5}
        assert gridschema.get_default_dataframe().equals(
            pd.DataFrame(
                [{"String": "string", "Floater": 1.5}],
                columns=pd.Index(["String", "Floater"], name="title"),
            )
        )

    def test_multiindex(self):
        class TestProperties(BaseModel):
            string: str = Field(json_schema_extra=dict(column_width=100, section="a"))
            floater: float = Field(
                1.5, json_schema_extra=dict(column_width=70, global_decimal_places=3, section="b")
            )
            inty: int = Field(1, json_schema_extra=dict(section="b"))

        class TestGridSchema(RootModel):
            """no default"""

            root: ty.List[TestProperties] = Field(
                [TestProperties(string="string").model_dump()],
                json_schema_extra=dict(format="dataframe", datagrid_index_name=("section", "title")),
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
        assert gridschema._get_default_data() == [
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
        
    def test_nullable_multiindex(self):
        class TestProperties(BaseModel):
            string: ty.Optional[str] = Field(json_schema_extra=dict(column_width=100, section="a"))
            floater: ty.Optional[float] = Field(
                1.5, json_schema_extra=dict(column_width=70, global_decimal_places=3, section="b")
            )
            inty: int = Field(1, json_schema_extra=dict(section="b"))

        class TestGridSchema(RootModel):
            """no default"""

            root: ty.List[TestProperties] = Field(
                [TestProperties(string="string").model_dump()],
                json_schema_extra=dict(format="dataframe", datagrid_index_name=("section", "title")),
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
        assert gridschema._get_default_data() == [
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
            string: str = Field(json_schema_extra=dict(column_width=100, section="a"))
            floater: float = Field(
                1.5, json_schema_extra=dict(column_width=70, global_decimal_places=3, section="b")
            )

        class TestGridSchema(RootModel):
            """no default"""

            root: ty.List[TestProperties] = Field(
                [TestProperties(string="string").model_dump()],
                json_schema_extra=dict(format="dataframe",
                datagrid_index_name=("section", "title")),
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
            string: str = Field(json_schema_extra=dict(column_width=100, section="a"))
            floater: float = Field(
                1.5, json_schema_extra=dict(column_width=70, global_decimal_places=3, section="b")
            )

        class TestGridSchema(RootModel):
            """no default"""

            root: ty.List[TestProperties] = Field(
                [TestProperties(string="string").model_dump()],
                json_schema_extra=dict(format="dataframe",
                datagrid_index_name=("section", "title")),
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
        df = pd.DataFrame.from_records(gridschema._get_default_data())
        data = gridschema.coerce_data(df)
        assert data.equals(df_check)
        assert gridschema.coerce_data(df, transposed=True).equals(df_check.T)

    def test_coerce_data_from_incomplete(self):
        class TestProperties(BaseModel):
            string: str
            floater: float = 1.5
            inty: int = 1

        class TestGridSchema(RootModel):
            """no default"""

            root: ty.List[TestProperties] = Field(
                [TestProperties(string="string").model_dump()],
                json_schema_extra=dict(format="dataframe"),
            )

        model, schema = _init_model_schema(TestGridSchema)
        gridschema = GridSchema(schema)
        data = gridschema.coerce_data(
            pd.DataFrame.from_dict({"string": ["asdf"], "floater": [1.0]})
        )

        assert list(data.columns) == [
            p["title"]
            for p in TestGridSchema.model_json_schema()["$defs"]["TestProperties"][
                "properties"
            ].values()
        ]

    def test_grid_types(self):
        class TestProperties(BaseModel):
            stringy: str
            floater: float = 1.5
            inty: int = 1

        class TestGridSchema(RootModel):
            """no default"""

            root: ty.List[TestProperties] = Field(
                [TestProperties(stringy="string").model_dump()],
                json_schema_extra=dict(format="dataframe"),
            )

        model, schema = _init_model_schema(TestGridSchema)
        gridschema = GridSchema(schema)
        data = gridschema.coerce_data(
            pd.DataFrame.from_dict({"stringy": ["asdf"], "floater": [1.0]})
        )

        assert gridschema.types == {
            "stringy": "string",
            "floater": "number",
            "inty": "integer",
        }


class TestAutoGrid:
    def test_empty_grid(self):
        class Cols(BaseModel):
            string: str = Field(json_schema_extra=dict(column_width=100))
            floater: float = Field(column_width=70, global_decimal_places=3)

        class DataFrameSchema(RootModel):
            """no default"""

            root: ty.List[Cols] = Field(format="dataframe")

        # initiate empty grid
        grid = AutoGrid(schema=DataFrameSchema)
        assert grid._data["data"] == []
        assert grid._data["schema"]["fields"] == [
            {"name": "index", "type": "integer"},  # NOTE: unable to detect type
            {"name": "String", "type": "string"},
            {"name": "Floater", "type": "string"},  # NOTE: unable to detect type
            {"name": "ipydguuid", "type": "integer"},
        ]

    def test_assign_default_at_root(self):
        # get default data from top-level schema defaults

        class Cols(BaseModel):
            string: str = Field("string", column_width=100)
            floater: float = Field(3.14, column_width=70, global_decimal_places=3)

        class DataFrameSchema(RootModel):
            """default."""

            root: ty.List[Cols] = Field(
                [Cols(string="test", floater=1.5).model_dump()], format="dataframe"
            )

        grid = AutoGrid(schema=DataFrameSchema)
        assert grid._data["data"] == [
            {"index": 0, "String": "test", "Floater": 1.5, "ipydguuid": 0}
        ]

    def test_pass_data_as_kwarg(self):
        # get default data passed as kwarg, titles as column headers
        class Cols(BaseModel):
            string: str = Field("string", json_schema_extra=dict(column_width=100))
            floater: float = Field(3.14, json_schema_extra=dict(column_width=70, global_decimal_places=3))

        class DataFrameSchema(RootModel):
            """no default. but properties have default"""

            root: ty.List[Cols] = Field(json_schema_extra=dict(format="dataframe"))

        df = pd.DataFrame([{"String": "test2", "Floater": 2.2}])
        grid3 = AutoGrid(schema=DataFrameSchema, data=df)
        assert grid3._data["data"] == [
            {"index": 0, "String": "test2", "Floater": 2.2, "ipydguuid": 0}
        ]

    def test_pass_data_as_kwarg_map_titles(self):
        # get default data passed as kwarg, keys as column headers. maps to titles

        class Cols(BaseModel):
            string: str = Field("string", json_schema_extra=dict(column_width=100))
            floater: float = Field(
                3.14,
                json_schema_extra=dict(column_width=70, global_decimal_places=3),
            )

        class DataFrameSchema(RootModel):
            """no default. but properties have default"""

            root: ty.List[Cols] = Field(json_schema_extra=dict(format="dataframe"))

        df = pd.DataFrame([{"string": "test2", "floater": 2.2}])
        grid = AutoGrid(schema=DataFrameSchema, data=df)
        assert grid._data["data"] == [
            {"index": 0, "String": "test2", "Floater": 2.2, "ipydguuid": 0}
        ]

    def test_reset_multiindex_data_with_init_data(self):
        # get default data passed as kwarg, keys as column headers. maps to titles

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

    @pytest.mark.parametrize("transposed", [True, False])
    def test_order_index(self, transposed: bool):
        """Test that the order works"""

        class Cols(BaseModel):
            string: str = Field(column_width=100)
            floater: float = Field(column_width=70, global_decimal_places=3)

        class DataFrameSchema(RootModel):
            """no default"""

            root: ty.List[Cols] = Field(format="dataframe")

        order = (
            "floater",
            "string",
        )
        # Test without data passed
        grid_without_data = AutoGrid(
            schema=DataFrameSchema, transposed=transposed, order=order
        )
        # Test with data passed
        data = pd.DataFrame([Cols(string="test", floater=2.5).model_dump()])
        grid_with_data = AutoGrid(
            schema=DataFrameSchema,
            data=data,
            transposed=transposed,
        )
        di_grid_with_data_before_order = grid_with_data.data.to_dict()
        grid_with_data.order = order
        if transposed:
            assert tuple(grid_without_data.data.index) == tuple(
                [grid_without_data.map_name_index.get(name) for name in order]
            )
            assert tuple(grid_with_data.data.index) == tuple(
                [grid_with_data.map_name_index.get(name) for name in order]
            )
            assert di_grid_with_data_before_order == grid_with_data.data.to_dict()
        else:
            assert tuple(grid_without_data.data.columns) == tuple(
                [grid_without_data.map_name_index.get(name) for name in order]
            )
            assert tuple(grid_with_data.data.columns) == tuple(
                [grid_with_data.map_name_index.get(name) for name in order]
            )
            assert di_grid_with_data_before_order == grid_with_data.data.to_dict()

    @pytest.mark.parametrize("transposed", [True, False])
    def test_order_multi_index(self, transposed: bool):
        """Test order with multi index"""

        class Cols(BaseModel):
            string: str = Field(column_width=100, title="String", section="a")
            floater: float = Field(
                column_width=70,
                global_decimal_places=3,
                title="Floater",
                section="a",
            )

        class DataFrameSchema(RootModel):
            """no default"""

            root: ty.List[Cols] = Field(
                format="dataframe",
                datagrid_index_name=("section", "title"),
            )

        order = (
            "floater",
            "string",
        )
        # Test without data passed
        grid_without_data = AutoGrid(schema=DataFrameSchema, order=order)
        # Test with data passed
        data = pd.DataFrame([Cols(string="test", floater=2.5).model_dump()])
        grid_with_data = AutoGrid(
            schema=DataFrameSchema,
            data=data,
            transposed=transposed,
        )
        di_grid_with_data_before_order = grid_with_data.data.to_dict()
        grid_with_data.order = order
        if transposed is True:
            assert tuple(grid_without_data.data.index) == ()
            assert tuple(grid_with_data.data.index) == tuple(
                [grid_with_data.map_name_index.get(name) for name in order]
            )
            assert di_grid_with_data_before_order == grid_with_data.data.to_dict()
        else:
            assert tuple(grid_without_data.data.columns) == tuple(
                [grid_without_data.map_name_index.get(name) for name in order]
            )
            assert tuple(grid_with_data.data.columns) == tuple(
                [grid_with_data.map_name_index.get(name) for name in order]
            )
            assert di_grid_with_data_before_order == grid_with_data.data.to_dict()

    @pytest.mark.parametrize("transposed", [True, False])
    def test_order_index_with_strict_subset(self, transposed: bool):
        """Test that the order is applied to the data even if the order is a strict subset of the data columns"""

        class Cols(BaseModel):
            string: str = Field(column_width=100)
            floater: float = Field(column_width=70, global_decimal_places=3)

        class DataFrameSchema(RootModel):
            """no default"""

            root: ty.List[Cols] = Field(format="dataframe")

        order = ("floater",)
        # Test without data passed
        grid_without_data = AutoGrid(
            schema=DataFrameSchema, transposed=transposed, order=order
        )
        # Test with data passed
        data = pd.DataFrame([Cols(string="test", floater=2.5).model_dump()])
        grid_with_data = AutoGrid(
            schema=DataFrameSchema,
            data=data,
            transposed=transposed,
        )
        di_grid_with_data_before_order = grid_with_data.data.to_dict()
        grid_with_data.order = order
        if transposed:
            assert tuple(grid_without_data.data.index) == tuple(
                [grid_without_data.map_name_index.get(name) for name in order]
            )
            assert tuple(grid_with_data.data.index) == tuple(
                [grid_with_data.map_name_index.get(name) for name in order]
            )
            assert di_grid_with_data_before_order.get(
                "Floater"
            ) == grid_with_data.data.to_dict().get("Floater")
        else:
            assert tuple(grid_without_data.data.columns) == tuple(
                [grid_without_data.map_name_index.get(name) for name in order]
            )
            assert tuple(grid_with_data.data.columns) == tuple(
                [grid_with_data.map_name_index.get(name) for name in order]
            )
            assert di_grid_with_data_before_order.get(
                "Floater"
            ) == grid_with_data.data.to_dict().get("Floater")

    @pytest.mark.parametrize("transposed", [True, False])
    def test_order_multi_index_with_strict_subset(self, transposed: bool):
        """Test that order works with multi-index and strict subset of columns"""

        class Cols(BaseModel):
            string: str = Field(column_width=100, title="String", section="a")
            floater: float = Field(
                column_width=70,
                global_decimal_places=3,
                title="Floater",
                section="a",
            )

        class DataFrameSchema(RootModel):
            """no default"""

            root: ty.List[Cols] = Field(
                format="dataframe",
                datagrid_index_name=("section", "title"),
            )

        order = ("floater",)
        # Test without data passed
        grid_without_data = AutoGrid(schema=DataFrameSchema, order=order)
        # Test with data passed
        data = pd.DataFrame([Cols(string="test", floater=2.5).model_dump()])
        grid_with_data = AutoGrid(
            schema=DataFrameSchema,
            data=data,
            transposed=transposed,
        )
        di_grid_with_data_before_order = grid_with_data.data.to_dict()
        grid_with_data.order = order
        if transposed is True:
            assert tuple(grid_without_data.data.index) == ()
            assert tuple(grid_with_data.data.index) == tuple(
                [grid_with_data.map_name_index.get(name) for name in order]
            )
            assert di_grid_with_data_before_order.get(
                ("a", "Floater")
            ) == grid_with_data.data.to_dict().get(("a", "Floater"))
        else:
            assert tuple(grid_without_data.data.columns) == tuple(
                [grid_without_data.map_name_index.get(name) for name in order]
            )
            assert tuple(grid_with_data.data.columns) == tuple(
                [grid_with_data.map_name_index.get(name) for name in order]
            )
            assert di_grid_with_data_before_order.get(
                ("a", "Floater")
            ) == grid_with_data.data.to_dict().get(("a", "Floater"))

    def test_records(self):
        """Test records method of AutoGrid. Also test that re-ordering indexes
        works correctly."""

        class Cols(BaseModel):
            string: str = Field(column_width=100)
            floater: float = Field(column_width=70, global_decimal_places=3)

        class DataFrameSchema(RootModel):
            """no default"""

            root: ty.List[Cols] = Field(format="dataframe")

        data = pd.DataFrame([Cols(string="test", floater=2.5).model_dump()])
        grid = AutoGrid(schema=DataFrameSchema, data=data)
        assert grid.records() == [{"string": "test", "floater": 2.5}]
        grid.order = ("floater", "string")
        assert grid.records() == [{"floater": 2.5, "string": "test"}]
        grid.order = ("floater",)
        assert grid.records() == [{"floater": 2.5}]
