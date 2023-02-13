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
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
"""defines a schema for a datagrid. this is used to build the datagrid and
contains methods for validation, coercion, and default values."""
# %run __init__.py
# %run ../__init__.py
# %load_ext lab_black
# TODO: move editgrid.py to root
import typing as ty
import logging
import pandas as pd
from pydantic import BaseModel, Field
from ipydatagrid import CellRenderer, TextRenderer
import ipyautoui.automapschema as asch
from ipyautoui._utils import obj_from_importstr, frozenmap

MAP_TRANSPOSED_SELECTION_MODE = frozenmap({True: "column", False: "row"})


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
    """Set the column widths of the data grid based on column_width given in the schema."""

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
class GridSchema:
    """
    this is inherited by AutoDataGrid. schema attributes are therefore set on the
    base class to ensure that when they are called the traits get set.

    Notes
    -----
        - this schema is valid only for an array (i.e. integer index) of objects
            the object names are the column names and the object values are the rows
        - data has 1no name based index (multi or otherwise) and 1no. integer index
        - the methods support "transposed" data. transposed is used to flip the
            dataframe to flip the view. the schema remains the same.
        - Gridschema handles converting between the user facing column names and the
            backend column names. this is done using `map_name_index` and `map_index_name`
            "index" is used for the front-end pandas dataframe column names
            "name" is used for the back-end keys


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
        self.validate_editable_grid_schema()
        if "datagrid_index_name" not in self.schema.keys():
            self.schema["datagrid_index_name"] = "title"

        self.index = self.get_index()
        self.get_traits = get_traits

        self.map_name_index = self.get_map_name_index()
        self.map_index_name = {v: k for k, v in self.map_name_index.items()}

        self.set_renderers(**kwargs)

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

    def set_renderers(self, **kwargs):
        {
            setattr(self, k, v)
            for k, v in get_global_renderers_from_schema(self.schema, **kwargs).items()
        }
        # ^ sets: ["default_renderer", "header_renderer", "corner_renderer"]
        self.renderers = get_column_renderers_from_schema(
            self.schema,
            column_properties=self.properties,
            map_name_index=self.map_name_index,
            **kwargs,
        )
        if len(self.renderers) == 0:
            self.renderers = None

    def validate_editable_grid_schema(self):
        """Check if the schema is valid for an editable grid"""
        if self.schema["type"] != "array":
            raise ValueError("Schema must be an array")
        if "items" not in self.schema.keys():
            raise ValueError("Schema must have an items property")
        if "properties" not in self.schema["items"].keys():
            raise ValueError("Schema must have an items.properties property")

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

    def get_index(self, order=None) -> ty.Union[pd.MultiIndex, pd.Index]:
        """Get pandas Index based on the data passed. The data index
        must be a subset of the gridschema index.

        Args:
            order (list): ordered columns

        Returns:
            Union[pd.MultiIndex, pd.Index]: pandas index
        """
        if self.is_multiindex:
            return pd.MultiIndex.from_tuples(
                self.get_field_names_from_properties(self.index_name, order=order),
                names=self.index_name,
            )
        else:
            return pd.Index(
                self.get_field_names_from_properties(self.index_name, order=order),
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

    def _get_default_data(self, order=None):
        if "default" in self.schema.keys():
            if order is None:
                return self.schema["default"]
            else:
                return [{k: v[k] for k in order} for v in self.schema["default"]]
        else:
            return []

    def _get_default_row(self):
        return get_default_row_data_from_schema_properties(
            self.properties, self.column_property_types
        )

    def get_default_dataframe(self, order=None, transposed=False):
        if len(self.default_data) == 0:
            df = pd.DataFrame(
                self.default_data, columns=self.index, index=pd.RangeIndex(0)
            )
        else:
            df = pd.DataFrame(self.default_data)
        return self.coerce_data(
            df,
            order=order,
            transposed=transposed,
        )

    @property
    def default_dataframe(self):
        if len(self.default_data) == 0:
            return pd.DataFrame(
                self.default_data, columns=self.index, index=pd.RangeIndex(0)
            )
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

    @property
    def default_order(self):
        return tuple(self.properties.keys())

    def get_order_titles(self, order):
        return [self.map_name_index[_] for _ in order]

    def get_field_names_from_properties(
        self, field_names: ty.Union[str, list], order: ty.Optional[tuple] = None
    ) -> list[ty.Union[tuple, str]]:
        if not order:
            order = self.default_order

        if isinstance(field_names, str):
            return [self.properties[_][field_names] for _ in order]
        else:
            return [
                tuple(self.properties[_][field_name] for field_name in field_names)
                for _ in list(order)
            ]

    @property
    def property_titles(self):
        return self.get_field_names_from_properties("title")

    def coerce_data(
        self, data: pd.DataFrame, order=None, transposed=False
    ) -> pd.DataFrame:
        """data must be passed with an integer index and columns matching the schema
        if transposed is True, the data will be transposed before getting passed to the grid

        Args:
            data (pd.DataFrame, optional): data to coerce. Defaults to None.

        Returns:
            pd.DataFrame: coerced data
        """

        if not isinstance(data.index, pd.RangeIndex):
            # raise ValueError("Data must have a RangeIndex")
            logging.warning("Data must have a RangeIndex")

        def is_bykeys(col_names):
            if set(col_names) <= set(self.map_name_index.keys()):
                return True
            elif set(col_names) <= set(self.map_index_name.keys()):
                return False
            else:
                raise ValueError(
                    "Columns must be a subset of the schema property keys or outward facing index names"
                )

        def filter_input_data(data, order, bykeys):
            if bykeys and len(col_names) > len(order):
                drop = [l for l in col_names if l not in order]
            else:
                drop = [l for l in col_names if l not in self.get_order_titles(order)]
            return data.drop(drop, axis=1)

        if order is None:
            order = self.default_order

        col_names = list(data.columns)
        bykeys = is_bykeys(col_names)

        # filter data as per order
        if len(col_names) > len(order):
            data = filter_input_data(data, order, bykeys)

        # map column names to outward facing names
        if bykeys:
            data = data.rename(
                columns={
                    k: v for k, v in self.map_name_index.items() if k in data.columns
                }
            )

        # ensure columns are in correct order
        data.columns = self.get_index(order)

        data.index = pd.RangeIndex(len(data))

        # transpose if necessary
        if transposed:
            data = data.T

        return data


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
