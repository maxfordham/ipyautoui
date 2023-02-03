# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
"""General widget for editing data"""
# %run __init__.py
# %run ../__init__.py
# %load_ext lab_black
# TODO: move editgrid.py to root
import traitlets as tr
import typing as ty
import logging
import traceback
import pandas as pd
import ipywidgets as w
from IPython.display import clear_output
from markdown import markdown
from pydantic import BaseModel, Field
from ipydatagrid import CellRenderer, DataGrid, TextRenderer
from ipydatagrid.datagrid import SelectionHelper

import ipyautoui.autoipywidget as aui
import ipyautoui.automapschema as asch
from ipyautoui.custom.buttonbars import CrudButtonBar
from ipyautoui._utils import obj_from_importstr, frozenmap
from ipyautoui.constants import BUTTON_WIDTH_MIN

MAP_TRANSPOSED_SELECTION_MODE = frozenmap({True: "column", False: "row"})
# TODO: rename "add" to "fn_add" so not ambiguous...

# +
def get_property_types(properties):
    def fn(t):
        if t == "number":
            t = "float"
        try:
            return eval(t)
        except:
            return str

    return {k: fn(v["type"])() for k, v in properties.items()}


# ui.schema
def get_default_row_data_from_schema_properties(
    properties: dict, property_types: dict
) -> ty.Optional[dict]:
    """pulls default value from schema. intended for a dataframe (i.e. rows
    of known columns only). assumes all fields have a 'title' (true when using
    pydantic)

    Args:
        properties (dict): schema["items"]["properties"]
        property_types (dict)

    Returns:
        dict: dictionary column values
    """
    get = lambda k, v: v["default"] if "default" in v.keys() else None
    di = {k: get(k, v) for k, v in properties.items()}
    return {k: v for k, v in di.items()}


def get_column_widths_from_schema(schema, column_properties, map_name_index, **kwargs):
    """Set the column widths of the data grid based on column_width given in the schema.
    """

    # start with settings in properties
    column_widths = {
        v["title"]: v["column_width"]
        for v in column_properties.values()
        if "column_width" in v
    }

    # override with high level schema props
    if "column_widths" in schema:
        column_widths = column_widths | schema["column_widths"]

    # overide with kwargs passed to AutoDataGrid
    if "column_widths" in kwargs:
        _ = {map_name_index[k]: v for k, v in kwargs["column_widths"].items()}
        column_widths = column_widths | _

    return column_widths


def build_renderer(var: ty.Union[str, dict]) -> CellRenderer:
    """builds a renderer for datagrid. if the input is a dict, the function assumes
    the renderer to use is `ipydatagrid.TextRenderer` and initiates it with the dict.
    This is appropriate for simple renderers only. If it is a string, it assumes that
    the renderer must be built by a zero-arg callable function that is referenced by an
    object string.

    Args:
        var (ty.Union[str, dict]): _description_
    """
    fn = lambda v: TextRenderer(**v) if isinstance(v, dict) else obj_from_importstr(v)()
    return fn(var)


def get_column_renderers_from_schema(
    schema, column_properties, map_name_index, **kwargs
) -> dict:
    """when saved to schema the renderer is a PyObject callable..."""

    # start with settings in properties
    renderers = {
        v["title"]: build_renderer(v["renderer"])
        for v in column_properties.values()
        if "renderer" in v
    }

    # override with high level schema props
    if "renderers" in schema:
        renderers = renderers | {k: build_renderer(v) for k, v in schema["renderers"]}

    # overide with kwargs passed to AutoDataGrid
    if "renderers" in kwargs:
        _ = {map_name_index[k]: v for k, v in kwargs["renderers"].items()}
        renderers = renderers | _

    return renderers


def get_global_renderer_from_schema(
    schema, renderer_name, **kwargs
) -> ty.Union[None, CellRenderer]:
    if renderer_name in kwargs:
        return kwargs[renderer_name]

    get_from_schema = lambda r, schema: schema[r] if r in schema.keys() else None
    _ = get_from_schema(renderer_name, schema)

    if _ is not None:
        return build_renderer(_)
    else:
        return None


def get_global_renderers_from_schema(schema, **kwargs) -> dict:
    li_renderers = ["default_renderer", "header_renderer", "corner_renderer"]
    # ^ globally specified ipydatagrid renderers
    renderers = {
        l: get_global_renderer_from_schema(schema, l, **kwargs) for l in li_renderers
    }
    return {k: v for k, v in renderers.items() if v is not None}


def is_incremental(li):
    return li == list(range(li[0], li[0] + len(li)))


# TODO: create an AutoUiSchema class to handle schema gen and then extend it here...
# TODO: consider extending by using pandera (schema defs and validation for pandas)
class GridSchema:
    """
    NOTE: index below can be either column index or row index. it can be swapped using
          transposed=True / False. the other index is always a range.
    """

    def __init__(self, schema, get_traits=None, **kwargs):
        """
        Args:
            schema: dict, jsonschema. must be array of properties
            get_traits: ty.Callable, passed from EditGrid to get a list of datagrid traits
            **kwargs: keyword args passed to datagrid on init
        """
        self.schema = schema
        if "datagrid_index_name" not in self.schema.keys():
            self.schema["datagrid_index_name"] = "title"
        else:
            self.schema["datagrid_index_name"] = tuple(
                self.schema["datagrid_index_name"]
            )
        self.index = self.get_index()
        self.get_traits = get_traits

        self.map_name_index = self.get_map_name_index()
        self.map_index_name = {v: k for k, v in self.map_name_index.items()}
        {
            setattr(self, k, v)
            for k, v in get_global_renderers_from_schema(self.schema, **kwargs).items()
        }
        # ^ sets: ["default_renderer", "header_renderer", "corner_renderer"]
        self.renderers = get_column_renderers_from_schema(
            schema,
            column_properties=self.properties,
            map_name_index=self.map_name_index,
            **kwargs,
        )
        if len(self.renderers) == 0:
            self.renderers = None
        self.column_widths = get_column_widths_from_schema(
            schema, self.properties, self.map_name_index, **kwargs
        )
        self.column_property_types = get_property_types(self.properties)
        self.default_data = self._get_default_data()
        self.default_row = self._get_default_row()

        # set any other kwargs ignoring ones that are handled above
        ignore_kwargs = [
            "default_renderer",
            "header_renderer",
            "corner_renderer",
            "renderers",
            "column_widths",
        ]
        {setattr(self, k, v) for k, v in kwargs.items() if k not in ignore_kwargs}

        # set any other field attributes ignoring ones that are handled above
        ignore_schema_keys = [
            "title",
            "format",
            "type",
            "items",
            "definitions",
        ]
        {
            setattr(self, k, v)
            for k, v in self.schema.items()
            if k not in ignore_schema_keys
        }

    @property
    def index_name(self):
        return self.schema["datagrid_index_name"]

    @property
    def is_multiindex(self):
        if isinstance(self.schema["datagrid_index_name"], tuple):
            return True
        else:
            return False

    def get_map_name_index(self):
        if not self.is_multiindex:
            return {k: v[self.index_name] for k, v in self.properties.items()}
        else:
            return {
                k: tuple(v[l] for l in self.index_name)
                for k, v in self.properties.items()
            }

    def get_index(self):
        if self.is_multiindex:
            return pd.MultiIndex.from_tuples(
                self.get_field_names_from_properties(self.index_name),
                names=self.index_name,
            )
        else:
            return pd.Index(
                self.get_field_name_from_properties(self.index_name),
                name=self.index_name,
            )

    @property
    def datagrid_traits(self) -> dict[str, ty.Any]:
        def try_getattr(obj, name):
            try:
                return getattr(obj, name)
            except:
                pass

        if self.get_traits is None:
            return {}
        else:
            _ = {t: try_getattr(self, t) for t in self.get_traits}
            return {k: v for k, v in _.items() if v is not None}

    def _get_default_data(self):
        if "default" in self.schema.keys():
            return self.schema["default"]
        else:
            return []

    def _get_default_row(self):
        row = get_default_row_data_from_schema_properties(
            self.properties, self.column_property_types
        )
        return row

    @property
    def default_dataframe(self):
        if len(self.default_data) == 0:
            return pd.DataFrame(self.default_data, columns=self.index)
        else:
            df = pd.DataFrame(self.default_data)
            df.columns = self.index
            return df

    @property
    def properties(self):
        return self.schema["items"]["properties"]

    @property
    def property_keys(self):
        return self.properties.keys()

    def get_field_name_from_properties(self, field_name: str) -> list:
        return [p[field_name] for p in self.properties.values()]

    def get_field_names_from_properties(self, li_field_names: list) -> list[tuple]:
        return [tuple(p[l] for l in li_field_names) for p in self.properties.values()]

    @property
    def property_titles(self):
        return self.get_field_name_from_properties("title")


# -


if __name__ == "__main__":

    class DataFrameCols(BaseModel):
        string: str = Field(
            "string",
            title="Important String",
            column_width=120,
        )
        integer: int = Field(40, title="Integer of somesort", column_width=150)
        floater: float = Field(
            1.3398234, title="Floater", column_width=70  # , renderer={"format": ".2f"}
        )

    class TestDataFrame(BaseModel):
        # dataframe: ty.List[DataFrameCols] = Field(..., format="dataframe")
        __root__: ty.List[DataFrameCols] = Field(
            ..., format="dataframe", global_decimal_places=2
        )

    model, schema = asch._init_model_schema(TestDataFrame)
    gridschema = GridSchema(schema)


class DataGrid(DataGrid):
    """extends DataGrid with useful generic functions"""

    global_decimal_places = tr.Int(default_value=None, allow_none=True)
    count_changes = tr.Int()

    @tr.default("count_changes")
    def _default_count_changes(self):
        self._observe_changes()
        return 0

    @tr.observe("global_decimal_places")
    def _global_decimal_places(self, change):
        newfmt = f".{str(self.global_decimal_places)}f"
        number_cols = [
            f["name"] for f in self.datagrid_schema_fields if f["type"] == "number"
        ]
        di = {}
        for col in number_cols:
            if col in self.renderers.keys():
                if self.renderers[col].format is None:  # no overwrite format if set
                    self.renderers[col].format = newfmt
            else:
                di[col] = TextRenderer(format=newfmt)
        self.renderers = self.renderers | di

    @property
    def datagrid_schema_fields(self):
        return self._data["schema"]["fields"]

    def _observe_changes(self):
        self.on_cell_change(self._count_cell_changes)
        self.observe(self._count_data_change, "_data")

    def _count_cell_changes(self, cell):
        logging.info(
            "DataGrid Change --> {row}:{column}".format(
                row=cell["row"], column=cell["column_index"]
            )
        )
        self.count_changes += 1

    def _count_data_change(self, cell):
        self.count_changes += 1

    def get_dataframe_index(self, dataframe):
        """Returns a primary key to be used in ipydatagrid's
        view of the passed DataFrame"""

        # Passed index_name takes highest priority
        if self._index_name is not None:
            return self._index_name

        # Dataframe with names index used by default
        if dataframe.index.name is not None:
            return dataframe.index.name

        # as above but for multi-index
        if dataframe.index.names is not None:
            return dataframe.index.names

        # If no index_name param, nor named-index DataFrame
        # have been passed, revert to default "key"
        return "key"

    # ----------------
    # https://github.com/bloomberg/ipydatagrid/issues/340
    # selecting when a transform is applied...
    @property
    def selected_visible_cell_iterator(self):
        """
        An iterator to traverse selected cells one by one.
        """
        # Copy of the front-end data model
        view_data = self.get_visible_data()

        # Get primary key from dataframe
        index_key = self.get_dataframe_index(view_data)

        # Serielize to JSON table schema
        view_data_object = self.generate_data_object(view_data, "ipydguuid", index_key)

        return SelectionHelper(view_data_object, self.selections, self.selection_mode)

    # these terms (below) avoid row or col terminology and can be used if transposed or not...
    # only these methods are called be EditGrid, allowing it to operate the same if the
    # view is transposed or not.
    # ----------


# +
# datagrid_index = "title"


class AutoGrid(DataGrid):
    """a thin wrapper around DataGrid that makes makes it possible to initiate the
    grid from a json-schema / pydantic model.

    Traits that can be set in a DataGrid instance can be reviewed using gr.traits().
    Note that of these traits, `column_widths` and `renderers` have the format
    {'column_name': <setting>}.

    NOTE:
    - Currently only supports a range index (or transposed therefore range columns)

    """

    schema = tr.Dict()
    transposed = tr.Bool(default_value=False)

    @tr.observe("schema")
    def _update_from_schema(self, change):
        self.gridschema = GridSchema(self.schema, **self.kwargs)

    @tr.validate("schema")
    def _valid_schema(self, proposal):
        if "type" in proposal["value"] and proposal["value"]["type"] == "array":
            if (
                "items" in proposal["value"]
                and "properties" in proposal["value"]["items"]
            ):
                return proposal["value"]
            else:
                raise tr.TraitError("schema have items and properties")
        else:
            raise tr.TraitError('schema must be of of type == "array"')

    @tr.observe("transposed")
    def _transposed(self, change):
        self.selection_mode = MAP_TRANSPOSED_SELECTION_MODE[change["new"]]
        if change["new"]:
            dft = self.data.T
            dft.index = self.gridschema.index
            if len(dft.columns) == 0:  # i.e. no data
                logging.info(
                    "ipydatagrid does not support dataframes with no columns. adding a"
                    " column with default row data"
                )
                dft = pd.DataFrame(
                    index=dft.index, columns=[0], data={0: self.default_row_title_keys}
                )
            self.data = dft
        else:
            dft = self.data.T
            dft.columns = self.gridschema.index
            self.data = dft
        # TODO: add method to allow for the setting/reverting of layout on change here...

    @property
    def is_transposed(self):
        if self.by_title:
            cols_check = self.gridschema.property_titles
        else:
            cols_check = self.gridschema.property_keys
        if set(cols_check) == set(self.column_names):
            return False
        else:
            return True

    def records(self, keys_as_title=False):
        if self.transposed:
            data = self.data.T
        else:
            data = self.data
        if keys_as_title:
            return data.to_dict(orient="records")
        else:
            data.columns = self.gridschema.property_keys
            return data.to_dict(orient="records")

    def __init__(
        self,
        schema: ty.Union[dict, ty.Type[BaseModel]],
        data: ty.Optional[pd.DataFrame] = None,
        by_alias: bool = False,
        by_title: bool = True,
        **kwargs,
    ):
        # accept schema or pydantic schema
        self.kwargs = (
            kwargs  # NOTE: kwargs are set from self.gridschema.datagrid_traits below...
        )
        self.by_title = by_title
        self.selection_mode = MAP_TRANSPOSED_SELECTION_MODE[self.transposed]
        self.model, self.schema = asch._init_model_schema(schema, by_alias=by_alias)
        self.gridschema.get_traits = self.datagrid_trait_names
        super().__init__(self._init_data(data))
        {setattr(self, k, v) for k, v in self.gridschema.datagrid_traits.items()}

        # annoyingly have to add this due to renderers being overwritten...
        if "global_decimal_places" in self.gridschema.datagrid_traits.keys():
            self.global_decimal_places = self.gridschema.datagrid_traits[
                "global_decimal_places"
            ]
        assert self.count_changes == 0
        # ^ this sets the default value and initiates change observer

    @property
    def default_row(self):
        return self.gridschema.default_row

    @property
    def default_row_title_keys(self):
        return {
            self.gridschema.map_name_index[k]: v
            for k, v in self.gridschema.default_row.items()
        }

    @property
    def datagrid_trait_names(self):
        return [l for l in self.trait_names() if l[0] != "_" and l != "schema"]

    @property
    def properties(self):
        return self.gridschema.properties

    @property
    def map_name_index(self):
        return self.gridschema.map_name_index

    @property
    def map_index_name(self):
        return self.gridschema.map_index_name

    @property
    def index_names(self):
        pass  # TODO: add this?

    @property
    def column_names(self):
        return self._get_col_headers(self._data)

    def get_col_name_from_index(self, index):
        return self.column_names[index]

    def get_index_based_on_data(self, data):
        """Get pandas Index based on the data passed. The data index
        must be a subset of the gridschema index.

        Args:
            data (pd.DataFrame): pandas dataframe of data related to schema

        Returns:
            Union[pd.MultiIndex, pd.Index]: pandas index
        """
        if self.gridschema.is_multiindex:
            return pd.MultiIndex.from_tuples(
                [self.gridschema.map_name_index.get(v) for v in data.columns],
                names=self.gridschema.index_name,
            )
        else:
            return pd.Index(
                [self.gridschema.map_name_index.get(v) for v in data.columns],
                name=self.gridschema.index_name,
            )

    def map_column_index_to_data(self, data):
        map_transposed = {True: "index", False: "columns"}
        working_index = map_transposed[self.transposed]  # either "index" or "columns
        if set(getattr(data, working_index)) == set(self.map_name_index.keys()):
            setattr(data, working_index, self.gridschema.index)
            return data
        elif set(getattr(data, working_index)) < set(self.map_name_index.keys()):
            setattr(data, working_index, self.get_index_based_on_data(data=data))
            return data  # .rename(columns=self.map_name_index)
        elif set(getattr(data, working_index)).issubset(
            set(self.map_name_index.values())
        ):
            return data  # i.e. using prperty key not title field... improve this...
        else:
            raise ValueError("input data does not match specified schema")

    def get_default_data(self):
        data = pd.DataFrame(self.gridschema.default_data)
        if self.by_title:
            data = data.rename(columns=self.map_name_index)
        return data

    def _init_data(self, data) -> pd.DataFrame:
        if data is None:
            return self.gridschema.default_dataframe
        else:
            data = data.copy(deep=True)
            if self.transposed:
                data = data.T

            return self.map_column_index_to_data(data)

    def set_cell_value_if_different(self, column_name, primary_key_value, new_value):
        old = self.get_cell_value(column_name, primary_key_value)
        if len(old) != 1:
            raise ValueError(
                f"multiple values return from: self.get_cell_value({column_name},"
                f" {primary_key_value})"
            )
        else:
            old = old[0]
        if old != new_value:
            s = (
                f"(column_name={column_name}, primary_key_value={primary_key_value})"
                f" old={old}, new={new_value})"
            )
            logging.info(s)
            print(s)
            self.set_cell_value(column_name, primary_key_value, new_value)
            return {
                "column_name": column_name,
                "primary_key_value": primary_key_value,
                "new_value": new_value,
            }
        else:
            pass

    def set_item_value(self, index: int, value: dict):
        """
        set row (transposed==False) or col (transposed==True) value
        """
        if self.transposed:
            return self.set_col_value(index, value)
        else:
            return self.set_row_value(index, value)

    def set_row_value(self, index: int, value: dict):
        """Set a chosen row using the key and a value given.

        Args:
            index (int): The key of the row. # TODO: is this defo an int?
            value (dict): The data we want to input into the row.
        """
        if set(value.keys()).issubset(set(self.map_name_index.keys())):
            # value_with_titles is used for datagrid
            value = {self.map_name_index.get(name): v for name, v in value.items()}
            # ^ self.apply_map_name_title(value)  ? ??
        elif set(value.keys()) == set(self.map_name_index.values()):
            pass
        else:
            raise Exception("Columns of value given do not match with value keys.")
        changes = [
            self.set_cell_value_if_different(column, index, v)
            for column, v in value.items()
        ]
        return [c for c in changes if c is not None]

    def apply_map_name_title(self, row_data):
        return {
            self.map_index_name[k]: v
            for k, v in row_data.items()
            if k in self.map_index_name.keys()
        }

    def set_col_value(self, index: int, value: dict):
        """Set a chosen col using the key and a value given.

        Note: We do not call value setter to apply values as it resets the datagrid.

        Args:
            key (int): The key of the col
            value (dict): The data we want to input into the col.
        """
        column_name = self.get_col_name_from_index(index)
        if set(value.keys()) == set(self.map_name_index.keys()):
            # value_with_titles is used for datagrid
            value = {self.map_name_index.get(name): v for name, v in value.items()}
        if set(value.keys()) != set(self.data.index.to_list()):
            raise Exception("Index of datagrid does not match with value keys.")
        changes = []
        for primary_key_value, v in value.items():
            if isinstance(primary_key_value, tuple):
                primary_key_value = list(primary_key_value)
            changes.append(
                self.set_cell_value_if_different(column_name, primary_key_value, v)
            )
        return [c for c in changes if c is not None]

    def filter_by_column_name(self, column_name: str, li_filter: list):
        """Filter rows to display based on a column name and a list of objects belonging to that column.

        Args:
            column_name (str): column name we want to apply the transform to.
            li_filter (list): Values within the column we want to display in the grid.
        """
        self.transform(
            [
                {
                    "type": "filter",
                    "columnIndex": self.data.columns.get_loc(column_name) + 1,
                    "operator": "in",
                    "value": li_filter,
                }
            ]
        )

    # move indexes around
    # ----------------
    def map_value_keys_index_name(self, value: dict) -> dict:
        """Checks if the keys of the dictionary are using the original field
        names and, if not, returns a new dict using the original field names.

        Args:
            value (dict): dictionary (potentially) using index names

        Returns:
            dict: New dictionary of same values but using original field names
        """
        if not set(value.keys()).issubset(set(self.gridschema.property_keys)):
            return {self.map_index_name.get(k): v for k, v in value.items()}
        else:
            return value

    def _swap_indexes(self, index_a: int, index_b: int):
        """Swap two indexes by giving their indexes.

        Args:
            index_a (int): index of a index.
            index_b (int): index of another index.
        """
        if self.transposed is False:
            di_a = self.map_value_keys_index_name(self.data.loc[index_a].to_dict())
            di_b = self.map_value_keys_index_name(self.data.loc[index_b].to_dict())
            self.set_row_value(index=index_b, value=di_a)
            self.set_row_value(index=index_a, value=di_b)
        else:
            di_a = self.map_value_keys_index_name(self.data.loc[:, index_a].to_dict())
            di_b = self.map_value_keys_index_name(self.data.loc[:, index_b].to_dict())
            self.set_col_value(index=index_b, value=di_a)
            self.set_col_value(index=index_a, value=di_b)

    def _move_index_down(self, index: int):
        """Move an index down numerically e.g. 1 -> 0

        Args:
            index (int): index of the index
        """
        if index - 1 == -1:
            raise Exception("Can't move down last index.")
        self._swap_indexes(index_a=index, index_b=index - 1)

    def _move_index_up(self, index: int):
        """Move an index up numerically e.g. 1 -> 2.

        Args:
            index (int): index of the index
        """
        if index + 1 == len(self.data):
            raise Exception("Can't move up first index.")
        self._swap_indexes(index_a=index, index_b=index + 1)

    def _move_indexes_up(self, li_indexes: ty.List[int]):
        """Move multiple indexes up numerically.

        Args:
            li_indexes (ty.List[int]): ty.List of index indexes.
        """
        self.clear_selection()
        if is_incremental(sorted(li_indexes)) is False:
            raise Exception("Only select a property or block of properties.")
        for index in sorted(li_indexes, reverse=True):
            self._move_index_up(index)
        self.selections = [
            {"r1": min(li_indexes) + 1, "r2": max(li_indexes) + 1, "c1": 0, "c2": 2}
        ]

    def _move_indexes_down(self, li_indexes: ty.List[int]):
        """Move multiple indexes down numerically.

        Args:
            li_indexes (ty.List[int]): ty.List of index indexes.
        """
        self.clear_selection()
        if is_incremental(sorted(li_indexes)) is False:
            raise Exception("Only select a property or block of properties.")
        for index in sorted(li_indexes):
            self._move_index_down(index)
        self.selections = [
            {"r1": min(li_indexes) - 1, "r2": max(li_indexes) - 1, "c1": 0, "c2": 2}
        ]

    # ----------------

    @property
    def selected(self):
        if self.transposed:
            return self.selected_col
        else:
            return self.selected_row

    @property
    def selected_items(self):
        if self.transposed:
            return self.selected_cols
        else:
            return self.selected_rows

    @property
    def selected_index(self):
        try:
            return self.selected_indexes[0]
        except:
            return None

    @property
    def selected_indexes(self):
        if self.transposed:
            return self.selected_col_indexes
        else:
            return self.selected_row_indexes

    # ----------

    @property
    def selected_row(self):
        """Get the data selected in the table which is returned as a dataframe."""
        try:
            return self.selected_rows[0]
        except:
            return None

    @property
    def selected_rows(self):
        """Get the data selected in the table which is returned as a dataframe."""
        s = self.selected_visible_cell_iterator
        rows = set([l["r"] for l in s])
        return [self.apply_map_name_title(s._data["data"][r]) for r in rows]

    @property
    def selected_col(self):
        """Get the data selected in the table which is returned as a dataframe."""
        try:
            return self.selected_cols[0]
        except:
            return None

    @property
    def selected_cols(self):
        """Get the data selected in the table which is returned as a dataframe."""
        di = self.selected_dict
        index = self.get_dataframe_index(self.data)
        if isinstance(index, pd.core.indexes.frozen.FrozenList):
            index = tuple(index)
        return [self.apply_map_name_title(v) for v in di.values()]

    @property
    def selected_row_index(self) -> ty.Any:
        try:
            return self.selected_row_indexes[0]
        except:
            return None

    @property
    def selected_row_indexes(self):
        """Return the indexes of the selected rows. still works if transform applied."""
        s = self.selected_visible_cell_iterator
        index = self.get_dataframe_index(self.data)
        if isinstance(index, pd.core.indexes.frozen.FrozenList):
            index = tuple(index)
        rows = set([l["r"] for l in s])
        return [s._data["data"][r][index] for r in rows]

    @property
    def selected_col_index(self):
        """returns the first."""
        return self.selected_col_indexes[0]

    @property
    def selected_col_indexes(self):
        """Return the indexes of the selected rows. still works if transform applied."""
        s = self.selected_visible_cell_iterator
        return list(set([l["c"] for l in s]))

    @property
    def selected_dict(self):
        """Return the dictionary of selected rows where index is row index. still works if transform applied.
        """
        if self.transposed:
            return self.data.T.loc[self.selected_col_indexes].to_dict("index")
        else:
            return self.data.loc[self.selected_row_indexes].to_dict("index")

    # ----------------


# -

if __name__ == "__main__":

    class DataFrameCols(BaseModel):
        string: str = Field(
            "string",
            title="Important String",
            column_width=120,
        )
        integer: int = Field(40, title="Integer of somesort", column_width=150)
        floater: float = Field(
            1.3398234, title="Floater", column_width=70  # , renderer={"format": ".2f"}
        )

    class TestDataFrame(BaseModel):
        # dataframe: ty.List[DataFrameCols] = Field(..., format="dataframe")
        __root__: ty.List[DataFrameCols] = Field(
            # [DataFrameCols()], format="dataframe", global_decimal_places=2
            format="dataframe",
            global_decimal_places=2,
        )

    grid = AutoGrid(schema=TestDataFrame, by_title=True)
    display(grid)


if __name__ == "__main__":

    class DataFrameCols(BaseModel):
        string: str = Field(
            title="Important String",
            column_width=120,
        )
        integer: int = Field(title="Integer of somesort", column_width=150)
        floater: float = Field(
            title="Floater", column_width=70  # , renderer={"format": ".2f"}
        )

    class TestDataFrame(BaseModel):
        __root__: ty.List[DataFrameCols] = Field(
            [
                DataFrameCols(string="string", integer=1, floater=1.2),
                DataFrameCols(string="another string", integer=10, floater=2.5),
                DataFrameCols(string="test", integer=42, floater=0.78),
            ],
            format="dataframe",
            global_decimal_places=2,
        )

    grid = AutoGrid(schema=TestDataFrame, by_title=True)
    display(grid)

if __name__ == "__main__":
    grid.data = pd.DataFrame(grid.data.to_dict(orient="records") * 4)  # .T

if __name__ == "__main__":
    print(grid.is_transposed)

if __name__ == "__main__":
    grid.transposed = True

if __name__ == "__main__":
    grid.set_item_value(0, {"string": "check", "integer": 2, "floater": 3.0})

if __name__ == "__main__":
    # test pd.to_dict
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    display(df)
    # ('dict', list, 'series', 'split', 'records', 'index')
    print(df.to_dict(orient="dict"))
    print(df.to_dict(orient="list"))
    # print(df.to_dict(orient="series", into=dict))
    print(df.to_dict(orient="split"))
    print(df.to_dict(orient="records"))
    print(df.to_dict(orient="index"))

if __name__ == "__main__":
    print(grid.count_changes)

if __name__ == "__main__":

    class DataFrameCols(BaseModel):
        string: str = Field(
            "string", title="Important String", column_width=120, section="a"
        )
        integer: int = Field(
            40, title="Integer of somesort", column_width=150, section="a"
        )
        floater: float = Field(
            1.3398234,
            title="Floater",
            column_width=70,
            section="b",  # , renderer={"format": ".2f"}
        )

    class TestDataFrame(BaseModel):
        # dataframe: ty.List[DataFrameCols] = Field(..., format="dataframe")
        __root__: ty.List[DataFrameCols] = Field(
            [DataFrameCols()],
            format="dataframe",
            global_decimal_places=2,
            datagrid_index_name=("section", "title"),
        )

    grid = AutoGrid(schema=TestDataFrame, by_title=True)
    display(grid)

if __name__ == "__main__":
    grid.data = pd.DataFrame(grid.data.to_dict(orient="records") * 4)

if __name__ == "__main__":
    grid.transposed = False

if __name__ == "__main__":
    grid.set_item_value(0, {"string": "check", "integer": 2, "floater": 3.0})


class DataHandler(BaseModel):
    fn_get_all_data: ty.Callable  # TODO: rename to fn_get
    fn_post: ty.Callable
    fn_patch: ty.Callable
    fn_delete: ty.Callable
    fn_copy: ty.Callable


if __name__ == "__main__":

    class TestModel(BaseModel):
        string: str = Field("string", title="Important String")
        integer: int = Field(40, title="Integer of somesort")
        floater: float = Field(1.33, title="floater")

    def test_save():
        print("Saved.")

    def test_revert():
        print("Reverted.")

    ui = aui.AutoObject(schema=TestModel)
    display(ui)

if __name__ == "__main__":
    ui.show_savebuttonbar = True
    display(ui.value)

if __name__ == "__main__":
    ui.value = {"string": "adfs", "integer": 2, "floater": 1.22}


class RowEditor:
    fn_add: ty.List[ty.Callable[[ty.Any, dict], None]]  # post
    fn_edit: ty.List[ty.Callable[[ty.Any, dict], None]]  # patch
    fn_move: ty.Callable
    fn_copy: ty.Callable
    fn_delete: ty.Callable


# +
class UiDelete(w.HBox):
    value = tr.Dict(default_value={})
    columns = tr.List(allow_none=True, default_value=None)

    @tr.observe("value")
    def observe_value(self, on_change):
        self._update_display()

    @tr.observe("columns")
    def observe_columns(self, on_change):
        if self.columns is not None:
            self.message_columns.value = f"columns shown: {str(self.columns)}"
        else:
            self.message_columns.value = "---"
        self._update_display()

    @property
    def value_summary(self):
        if self.columns is not None:
            return {
                k: {k_: v_ for k_, v_ in v.items() if k_ in self.columns}
                for k, v in self.value.items()
            }
        else:
            return self.value

    def _update_display(self):
        with self.out_delete:
            clear_output()
            display(self.value_summary)

    def __init__(self, fn_delete: ty.Callable = lambda: print("delete"), **kwargs):
        super().__init__(**kwargs)
        self.fn_delete = fn_delete
        self.out_delete = w.Output()
        self.bn_delete = w.Button(
            icon="exclamation-triangle",
            button_style="danger",
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.vbx_messages = w.VBox()
        self.message = w.HTML(
            "⚠️<b>warning</b>⚠️ - <i>pressing button will permanently delete rows from"
            " grid</i>"
        )
        self.message_columns = w.HTML(f"---")
        self.vbx_messages.children = [
            self.message,
            self.message_columns,
            self.out_delete,
        ]
        self.children = [self.bn_delete, self.vbx_messages]
        self._init_controls()

    def _init_controls(self):
        self.bn_delete.on_click(self._bn_delete)

    def _bn_delete(self, onclick):
        self.fn_delete()


if __name__ == "__main__":
    delete = UiDelete()
    display(delete)
# -

if __name__ == "__main__":
    delete.value = {"key": {"col1": "value1", "col2": "value2"}}


# +
class UiCopy(w.HBox):
    index = tr.Integer()  # row index copying from... improve user reporting

    def __init__(
        self,
        fn_copy_beginning: ty.Callable = lambda: print(
            "duplicate selection to beginning"
        ),
        fn_copy_inplace: ty.Callable = lambda: print(
            "duplicate selection to below current"
        ),
        fn_copy_end: ty.Callable = lambda: print("duplicate selection to end"),
        fn_copy_to_selection: ty.Callable = lambda: print(
            "select new row/col to copy to"
        ),
        transposed: bool = False,
    ):
        super().__init__()
        self.fn_copy_beginning = fn_copy_beginning
        self.fn_copy_inplace = fn_copy_inplace
        self.fn_copy_end = fn_copy_end
        self.fn_copy_to_selection = fn_copy_to_selection
        self.map_action = {
            "duplicate selection to beginning": self.fn_copy_beginning,
            "duplicate selection to below current": self.fn_copy_inplace,
            "duplicate selection to end": self.fn_copy_end,
            "select new row/col to copy to": self.fn_copy_to_selection,
        }
        self.ui_copytype = w.RadioButtons(
            options=list(self.map_action.keys()),
            value="duplicate selection to end",
        )
        self.bn_copy = w.Button(
            icon="copy",
            button_style="success",
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.vbx_messages = w.VBox()
        self.message = w.HTML("ℹ️ <b>Note</b> ℹ️ - <i>copy data from selected row")
        self.message_columns = w.HTML(f"---")
        self.vbx_messages.children = [
            self.message,
            self.message_columns,
            self.ui_copytype,
        ]
        self.children = [self.bn_copy, self.vbx_messages]
        self._init_controls()

    def _init_controls(self):
        self.bn_copy.on_click(self._bn_copy)

    def _bn_copy(self, onclick):
        self.map_action[self.ui_copytype.value]()


if __name__ == "__main__":
    display(UiCopy())


# -


class EditGrid(w.VBox):
    _value = tr.Tuple()  # using a tuple to guarantee no accidental mutation
    warn_on_delete = tr.Bool()
    show_copy_dialogue = tr.Bool()
    close_crud_dialogue_on_action = tr.Bool()

    @tr.observe("warn_on_delete")
    def observe_warn_on_delete(self, on_change):
        if self.warn_on_delete:
            self.ui_delete.layout.display = ""
        else:
            self.ui_delete.layout.display = "None"

    @tr.observe("show_copy_dialogue")
    def observe_show_copy_dialogue(self, on_change):
        if self.show_copy_dialogue:
            self.ui_copy.layout.display = ""
        else:
            self.ui_copy.layout.display = "None"

    @property
    def value(self):
        return self._value

    @property
    def transposed(self):
        return self.grid.transposed

    @transposed.setter
    def transposed(self, value: bool):
        self.grid.transposed = value

    def _update_value_from_grid(self):
        self._value = self.grid.records()

    @value.setter
    def value(self, value):
        if value == [] or value is None:
            self.grid.data = self.grid.get_default_data()
        else:
            self.grid.data = self.grid._init_data(pd.DataFrame(value))

        # HOTFIX: Setting data creates bugs out transforms currently so reset transform applied
        _transforms = self.grid._transforms
        self.grid.transform([])  # Set to no transforms
        self.grid.transform(_transforms)  # Set to previous transforms

    def __init__(
        self,
        schema: ty.Union[dict, ty.Type[BaseModel]],
        value: ty.Optional[list[dict[str, ty.Any]]] = None,
        by_alias: bool = False,
        by_title: bool = True,
        datahandler: ty.Optional[DataHandler] = None,
        ui_add: ty.Optional[ty.Callable] = None,
        ui_edit: ty.Optional[ty.Callable] = None,
        ui_delete: ty.Optional[ty.Callable] = None,
        ui_copy: ty.Optional[ty.Callable] = None,
        warn_on_delete: bool = False,
        show_copy_dialogue: bool = False,
        close_crud_dialogue_on_action: bool = False,
        description: str = "",
        **kwargs,
    ):
        self.description = w.HTML(description)
        self.by_title = by_title
        self.by_alias = by_alias
        self.datahandler = datahandler
        self.grid = AutoGrid(schema, value=value, by_alias=self.by_alias, **kwargs)

        self._init_form()
        if ui_add is None:
            self.ui_add = AutoObjectFiltered(self.row_schema, app=self)
        else:
            self.ui_add = ui_add(self.row_schema, app=self)
        if ui_edit is None:
            self.ui_edit = AutoObjectFiltered(self.row_schema, app=self)
        else:
            self.ui_edit = ui_edit(self.row_schema, app=self)
        if ui_delete is None:
            self.ui_delete = UiDelete()
        else:
            self.ui_delete = ui_delete()
        self.ui_delete.layout.display = "None"
        if ui_copy is None:
            self.ui_copy = UiCopy()
        else:
            self.ui_copy = ui_copy()
        self.ui_copy.layout.display = "None"
        self.warn_on_delete = warn_on_delete
        # self.show_copy_dialogue = show_copy_dialogue
        self.show_copy_dialogue = False
        # ^ TODO: delete this when that functionality is added
        self.close_crud_dialogue_on_action = close_crud_dialogue_on_action
        self.ui_delete.fn_delete = self._delete_selected
        self._update_value_from_grid()
        self._init_row_controls()
        self.stk_crud = w.Stack(
            children=[self.ui_add, self.ui_edit, self.ui_copy, self.ui_delete]
        )
        self.children = [
            self.description,
            self.buttonbar_grid,
            self.stk_crud,
            self.grid,
        ]
        self._init_controls()

    def _init_row_controls(self):
        self.ui_edit.show_savebuttonbar = True
        self.ui_edit.savebuttonbar.fns_onsave = [self._patch, self._save_edit_to_grid]
        self.ui_edit.savebuttonbar.fns_onrevert = [self._set_ui_edit_to_selected_row]
        self.ui_add.show_savebuttonbar = True
        self.ui_add.savebuttonbar.fns_onsave = [self._post, self._save_add_to_grid]
        self.ui_add.savebuttonbar.fns_onrevert = [self._set_ui_add_to_default_row]

    @property
    def schema(self):
        return self.grid.schema

    @property
    def row_schema(self):
        return self.grid.schema["items"]

    @property
    def model(self):
        return self.grid.model

    def _init_form(self):
        super().__init__()
        self.buttonbar_grid = CrudButtonBar(
            add=self._add,
            edit=self._edit,
            copy=self._copy,
            delete=self._delete,
            # backward=self.setview_default,
            show_message=False,
        )
        self.addrow = w.VBox()
        self.editrow = w.VBox()

    def _init_controls(self):
        self.grid.observe(self._observe_selections, "selections")
        self.grid.observe(self._grid_changed, "count_changes")
        self.buttonbar_grid.observe(self._setview, "active")

    def _observe_selections(self, onchange):
        if self.buttonbar_grid.edit.value:
            self._set_ui_edit_to_selected_row()
        if self.buttonbar_grid.delete.value:
            self._set_ui_delete_to_selected_row()

    # @debounce(0.1)  # TODO: make debounce work if too slow...
    def _grid_changed(self, onchange):
        # debouncer used to allow editing whole rows in 1 go
        # without updating the `value` on every cell edit.
        self._update_value_from_grid()

    def _setview(self, onchange):
        if self.buttonbar_grid.active is None:
            self.stk_crud.selected_index = None
        else:
            self.stk_crud.selected_index = int(self.buttonbar_grid.active.value)

    def _check_one_row_selected(self):
        if len(self.grid.selected_indexes) > 1:
            raise Exception(
                markdown("  👇 _Please only select ONLY one row from the table!_")
            )

    # edit row
    # --------------------------------------------------------------------------
    def _validate_edit_click(self):
        if len(self.grid.selected_indexes) == 0:
            raise ValueError(
                "you must select an index (row if transposed==True, col if"
                " transposed==True)"
            )
        self._check_one_row_selected()

    def _save_edit_to_grid(self):
        changes = self.grid.set_item_value(self.grid.selected_index, self.ui_edit.value)
        # TODO: patch changes back to source
        if self.close_crud_dialogue_on_action:
            self.buttonbar_grid.edit.value = False

    def _set_ui_edit_to_selected_row(self):
        self.ui_edit.value = self.grid.selected
        self.ui_edit.savebuttonbar.unsaved_changes = False

    def _patch(self):
        if self.datahandler is not None:
            self.datahandler.fn_patch(self.ui_edit.value)

    def _edit(self):
        try:
            self._validate_edit_click()
            self._set_ui_edit_to_selected_row()

        except Exception as e:
            self.buttonbar_grid.edit.value = False
            self.buttonbar_grid.message.value = markdown(
                "  👇 _Please select one row from the table!_ "
            )
            traceback.print_exc()

    # --------------------------------------------------------------------------

    # add row
    # --------------------------------------------------------------------------
    def _save_add_to_grid(self):
        if not self.grid._data["data"]:  # If no data in grid
            self.value = tuple([self.ui_add.value])
        else:
            # Append new row onto data frame and set to grid's data.
            # Call setter. syntax below required to avoid editing in place.
            self.value = tuple(list(self.value) + [self.ui_add.value])
        if self.close_crud_dialogue_on_action:
            self.buttonbar_grid.add.value = False

    def _set_ui_add_to_default_row(self):
        if self.ui_add.value == self.grid.default_row:
            self.ui_add.savebuttonbar.unsaved_changes = False
        else:
            self.ui_add.savebuttonbar.unsaved_changes = True

    def _post(self):
        if self.datahandler is not None:
            self.datahandler.fn_post(self.ui_add.value)

    def _add(self):
        self._set_ui_add_to_default_row()

    # --------------------------------------------------------------------------

    # copy
    # --------------------------------------------------------------------------

    def _get_selected_data(self):  # TODO: is this required? is it dupe from DataGrid?
        if self.grid.selected_index is not None:
            li_values_selected = [
                self.value[i] for i in sorted([i for i in self.grid.selected_indexes])
            ]
        else:
            li_values_selected = []
        return li_values_selected

    def _copy_selected_inplace(self):
        pass

    def _copy_selected_to_beginning(self):
        pass

    def _copy_selected_to_end(self):
        self.value = tuple(list(self.value) + self._get_selected_data())
        if self.close_crud_dialogue_on_action:
            self.buttonbar_grid.copy.value = False

    def _copy(self):
        try:
            if self.grid.selected_indexes == []:
                self.buttonbar_grid.message.value = markdown(
                    "  👇 _Please select a row from the table!_ "
                )
            else:
                if not self.show_copy_dialogue:
                    if self.datahandler is not None:
                        for value in self._get_selected_data():
                            self.datahandler.fn_copy(value)
                        self._reload_all_data()
                    else:
                        self._copy_selected_to_end()
                        # ^ add copied values. note. above syntax required to avoid editing in place.

                    self.buttonbar_grid.message.value = markdown("  📝 _Copied Data_ ")
                    self.buttonbar_grid.copy.value = False

                else:
                    print("need to implement show copy dialogue")
        except Exception as e:
            self.buttonbar_grid.message.value = markdown(
                "  👇 _Please select a row from the table!_ "
            )
            traceback.print_exc()

    # --------------------------------------------------------------------------

    # delete
    # --------------------------------------------------------------------------
    def _reload_all_data(self):
        if self.datahandler is not None:
            self.value = self.datahandler.fn_get_all_data()

    def _delete_selected(self):
        if self.datahandler is not None:
            value = [self.value[i] for i in self.grid.selected_indexes]
            for v in value:
                self.datahandler.fn_delete(v)
            self._reload_all_data()
        else:
            self.value = [
                value
                for i, value in enumerate(self.value)
                if i not in self.grid.selected_indexes
            ]
            # ^ Only set for values NOT in self.grid.selected_indexes
        self.buttonbar_grid.message.value = markdown("  🗑️ _Deleted Row_ ")
        if self.close_crud_dialogue_on_action:
            self.buttonbar_grid.delete.value = False

    def _set_ui_delete_to_selected_row(self):
        logging.info(f"delete: {self.grid.selected_dict}")
        self.ui_delete.value = self.grid.selected_dict

    def _delete(self):
        try:
            if len(self.grid.selected_indexes) > 0:
                if not self.warn_on_delete:
                    self.buttonbar_grid.delete.value = False
                    self._delete_selected()
                else:
                    self.ui_delete.value = self.grid.selected_dict
            else:
                self.buttonbar_grid.delete.value = False
                self.buttonbar_grid.message.value = markdown(
                    "  👇 _Please select at least one row from the table!_"
                )

        except Exception as e:
            print("delete error")
            traceback.print_exc()


class AutoObjectFiltered(
    aui.AutoObject
):  # TODO: Implement into EditGrid class by default... !
    """This extended AutoObject class relies on EditGrid and a row_schema dictionary.

    The AutoObject will update its rows based on the visible rows of the grid.
    """

    def __init__(self, row_schema: dict, app: EditGrid, *args, **kwargs):
        self.row_schema = row_schema
        self.app = app
        self._selections = []
        super().__init__(row_schema, *args, **kwargs)
        self.app.grid.observe(self._update_order, "_visible_rows")
        self.app.grid.observe(
            self._save_previous_selections, "selections"
        )  # Re-apply selection after updating transforms

    def _get_visible_fields(self):
        """Get the list of fields that are visible in the DataGrid."""
        if isinstance(self.app.grid.get_visible_data().index, pd.MultiIndex) is True:
            title_idx = self.app.grid.get_visible_data().index.names.index("title")
            visible_titles = [
                v[title_idx] for v in self.app.grid.get_visible_data().index
            ]
            return [
                k
                for k, v in self.app.row_schema["properties"].items()
                if v["title"] in visible_titles
            ]
        elif isinstance(self.app.grid.get_visible_data().index, pd.Index) is True:
            return [
                k
                for k, v in self.app.row_schema["properties"].items()
                if v["title"] in self.app.grid.get_visible_data().index
            ]

        else:
            raise Exception("Index obtained not of correct type.")

    def _update_order(self, onchange):
        """Update order instance of AutoObject based on visible fields in the DataGrid.
        """
        if self.app.transposed is True:
            self.order = self._get_visible_fields()
            self.app.grid.selections = self._selections

    def _save_previous_selections(self, onchange):
        if self.app.grid.selections:
            self._selections = self.app.grid.selections


if __name__ == "__main__":
    # Test: EditGrid instance with multi-indexing.
    AUTO_GRID_DEFAULT_VALUE = [
        {
            "string": "important string",
            "integer": 1,
            "floater": 3.14,
        },
    ]
    AUTO_GRID_DEFAULT_VALUE = AUTO_GRID_DEFAULT_VALUE * 4

    class DataFrameCols(BaseModel):
        string: str = Field("string", column_width=100, section="a")
        integer: int = Field(1, column_width=80, section="a")
        floater: float = Field(None, column_width=70, aui_sig_fig=3, section="b")

    class TestDataFrame(BaseModel):
        """a description of TestDataFrame"""

        __root__: ty.List[DataFrameCols] = Field(
            default=AUTO_GRID_DEFAULT_VALUE,
            format="dataframe",
            datagrid_index_name=("section", "title"),
        )

    description = markdown(
        "<b>The Wonderful Edit Grid Application</b><br>Useful for all editing purposes"
        " whatever they may be 👍"
    )
    editgrid = EditGrid(
        schema=TestDataFrame,
        description=description,
        ui_add=None,
        ui_edit=None,
        warn_on_delete=True,
        show_copy_dialogue=False,
        close_crud_dialogue_on_action=False,
    )
    editgrid.observe(lambda c: print("_value changed"), "_value")
    display(editgrid)


if __name__ == "__main__":
    # Test: Using AutoObjectFiltered
    editgrid = EditGrid(
        schema=TestDataFrame,
        description=description,
        ui_add=AutoObjectFiltered,
        ui_edit=AutoObjectFiltered,
        warn_on_delete=True,
    )
    editgrid.observe(lambda c: print("_value changed"), "_value")
    editgrid.transposed = True
    display(editgrid)

if __name__ == "__main__":
    from ipyautoui.demo_schemas import CoreIpywidgets
    from ipyautoui.autoipywidget import AutoObject

    #     class TestDataFrame(BaseModel):
    #         """a description of TestDataFrame"""

    #         __root__: ty.List[CoreIpywidgets] = Field(
    #             [CoreIpywidgets().dict()], format="dataframe"
    #         )
    # TODO: ^ fix this

    class TestDataFrame(BaseModel):
        """a description of TestDataFrame"""

        __root__: ty.List[DataFrameCols] = Field(
            [
                DataFrameCols(
                    string="String",
                    integer=1,
                    floater=2.5,
                ).dict()
            ],
            format="dataframe",
        )

    description = markdown(
        "<b>The Wonderful Edit Grid Application</b><br>Useful for all editing purposes"
        " whatever they may be 👍"
    )
    editgrid = EditGrid(
        schema=TestDataFrame,
        description=description,
        ui_add=None,
        ui_edit=None,
        warn_on_delete=True,
    )
    editgrid.observe(lambda c: print("_value changed"), "_value")
    display(editgrid)

if __name__ == "__main__":
    editgrid.transposed = True

if __name__ == "__main__":

    class TestDataFrame(BaseModel):
        __root__: ty.List[DataFrameCols] = Field(
            default=AUTO_GRID_DEFAULT_VALUE, format="dataframe"
        )


if __name__ == "__main__":
    from ipyautoui import AutoUi
    from ipyautoui.autoipywidget import AutoObject

    ui = AutoObject(schema=TestDataFrame)
    ui.align_horizontal = True
    ui.auto_open = True
    ui.observe(lambda c: print("_value change"), "_value")
    ui.di_widgets["__root__"].observe(lambda c: print("grid _value change"), "_value")
    display(ui)
