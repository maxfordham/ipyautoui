
# +
"""defines a schema for a datagrid. this is used to build the datagrid and
contains methods for validation, coercion, and default values. 

defines AutoGrid, a datagrid generated from a jsonschema."""

import typing as ty
from copy import deepcopy
import logging
import pandas as pd

import traitlets as tr
from pydantic import BaseModel, Field
from ipydatagrid import CellRenderer, DataGrid, TextRenderer, VegaExpr
from ipydatagrid.datagrid import SelectionHelper

from ipyautoui.custom.datagrid import DataGrid
import ipyautoui.automapschema as asch
from ipyautoui._utils import obj_from_importstr, frozenmap
from ipyautoui._utils import json_as_type

MAP_TRANSPOSED_SELECTION_MODE = frozenmap({True: "column", False: "row"})


# +
def get_property_types(properties):  #  TODO: THIS SHOULD NOT BE REQUIRED
    def fn(v):
        if "type" in v:
            t = v["type"]
            try:
                return json_as_type(t)
            except:
                return str
        elif "anyOf" in v:
            types = [_.get("type") for _ in v["anyOf"] if _.get("type") != "null"]
            if len(types) == 1:
                t = types[0]
                return json_as_type(t)
            else:
                return lambda: None
        else:
            return lambda: None

    return {k: fn(v)() for k, v in properties.items()}


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
            "$defs",
        ]
        {
            setattr(self, k, v)
            for k, v in self.schema.items()
            if k not in ignore_schema_keys
        }
        self.default_row = self._get_default_row()

    @property
    def types(self):
        return {k: v["type"] for k, v in self.schema["items"]["properties"].items()}

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
        if isinstance(self.index_name, tuple) or isinstance(self.index_name, list):
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
        ind = self.get_field_names_from_properties(self.index_name, order=order)
        if self.is_multiindex:
            return pd.MultiIndex.from_tuples(ind, names=self.index_name)
        else:
            return pd.Index(ind, name=self.index_name)

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
        if len(self._get_default_data(order=order)) == 0:
            df = pd.DataFrame(
                self._get_default_data(order=order),
                columns=self.index,
                index=pd.RangeIndex(0),
            )
        else:
            df = pd.DataFrame(self._get_default_data(order=order))
        return self.coerce_data(
            df,
            order=order,
            transposed=transposed,
        )

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
            return [self.properties[_].get(field_names) for _ in order]
        else:
            return [
                tuple(self.properties[_].get(field_name) for field_name in field_names)
                for _ in list(order)
            ]

    @property
    def property_titles(self):
        return self.get_field_names_from_properties("title")

    def coerce_data(
        self, data: pd.DataFrame, order=None, transposed=False
    ) -> pd.DataFrame:
        """data must be passed with an integer index and columns matching the schema.
        Column names can be either the outward facing index names or the schema property keys.
        if transposed is True, the data will be transposed before getting passed to the grid

        Args:
            data (pd.DataFrame, optional): data to coerce

        Returns:
            pd.DataFrame: coerced data
        """

        if not isinstance(data.index, pd.RangeIndex):
            logging.warning(
                "ipyautoui.custom.autogrid.AutoGrid (and EditGrid) data must have a"
                " RangeIndex"
            )

        def is_bykeys(col_names):
            if set(col_names) <= set(self.map_name_index.keys()):
                return True
            elif set(col_names) <= set(self.map_index_name.keys()):
                return False
            else:
                raise ValueError(
                    "Columns must be a subset of the schema property keys or outward"
                    " facing index names"
                )

        def filter_input_data(data, order, bykeys):
            if bykeys and len(col_names) > len(order):
                drop = [l for l in col_names if l not in order]
            else:
                drop = [l for l in col_names if l not in self.get_order_titles(order)]
            return data.drop(drop, axis=1)

        def fill_with_default(col):
            default_value = self._get_default_row().get(col.name)
            if default_value is None:
                return col
            else:
                return col.apply(
                    lambda x: (
                        default_value
                        if (pd.isna(x).all() if isinstance(x, list) else pd.isna(x))
                        else x
                    )
                )

        if order is None:
            order = self.default_order

        col_names = list(data.columns)
        bykeys = is_bykeys(col_names)

        # filter data as per order
        if len(col_names) > len(order):
            data = filter_input_data(data, order, bykeys)

        if len(col_names) < len(order):
            # add missing columns
            if bykeys:
                data = data.reindex(columns=order)
            else:
                data = data.reindex(columns=[self.map_name_index[x] for x in order])

        data = data.apply(fill_with_default)

        # map column names to outward facing names
        if bykeys:
            data = data.rename(
                columns={
                    k: v for k, v in self.map_name_index.items() if k in data.columns
                }
            )

        # ensure columns are in correct order
        data = data.reindex(self.get_index(order), axis=1)
        data.index = pd.RangeIndex(len(data))

        # transpose if necessary
        if transposed:
            data = data.T

        return data


# -
if __name__ == "__main__":
    from pydantic import RootModel

    class DataFrameCols(BaseModel):
        string: str = Field(
            "string",
            title="Important String",
            json_schema_extra=dict(column_width=120),
        )
        integer: int = Field(
            40, title="Integer of somesort", json_schema_extra=dict(column_width=150)
        )
        floater: float = Field(
            1.3398234,
            title="Floater",
            json_schema_extra=dict(column_width=70),  # , renderer={"format": ".2f"}
        )

    class TestDataFrame(RootModel):
        root: ty.List[DataFrameCols] = Field(
            ..., json_schema_extra=dict(global_decimal_places=2, format="dataframe")
        )

    model, schema = asch._init_model_schema(TestDataFrame)
    gridschema = GridSchema(schema)


# +
# datagrid_index = "title"
# from ipyautoui.automapschema import from_schema_method


class AutoGrid(DataGrid):
    """a thin wrapper around DataGrid that makes makes it possible to initiate the
    grid from a json-schema / pydantic model.

    Traits that can be set in a DataGrid instance can be reviewed using gr.traits().
    Note that of these traits, `column_widths` and `renderers` have the format
    {'column_name': <setting>}.

    NOTE:
    - Currently only supports a range index (or transposed therefore range columns)

    """

    schema = tr.Dict(default_value=None, allow_none=True)
    order = tr.Tuple(default_value=None, allow_none=True)
    datagrid_index_name = tr.Union(trait_types=[tr.Unicode(), tr.Tuple()])

    @tr.observe("schema")
    def _set_gridschema(self, onchange):
        self.gridschema = GridSchema(self.schema, **self.kwargs)

    def update_from_schema(
        self,
        schema: ty.Optional[ty.Union[dict, ty.Type[BaseModel]]] = None,
        data: ty.Optional[pd.DataFrame] = None,
        by_alias: bool = False,
        by_title: bool = True,
        order: ty.Optional[tuple] = None,
        generate_pydantic_model_from_json_schema: bool = False,
        **kwargs,
    ):
        self.__init__(
            schema=schema,
            data=data,
            by_alias=by_alias,
            by_title=by_title,
            order=order,
            generate_pydantic_model_from_json_schema=generate_pydantic_model_from_json_schema,
            **kwargs,
        )

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

    @tr.observe("order")
    def _observe_order(self, change):
        if not set(self.order) <= set(self.gridschema.properties.keys()):
            raise ValueError(
                "set(self.order) <= set(self.gridschema.properties.keys()) must be"
                " true. (i.e. only valid scheam properties allowed)"
            )
        if self.transposed:
            data = self.data.T
        else:
            data = self.data
        data.index = pd.RangeIndex(0, len(data))
        self.data = self._init_data(data)

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
            data.columns = [
                self.gridschema.map_index_name.get(name) for name in data.columns
            ]
            return data.to_dict(orient="records")

    def __init__(
        self,
        schema: ty.Optional[ty.Union[dict, ty.Type[BaseModel]]] = None,
        data: ty.Optional[pd.DataFrame] = None,
        by_alias: bool = False,
        by_title: bool = True,
        order: ty.Optional[tuple] = None,
        generate_pydantic_model_from_json_schema: bool = False,
        **kwargs,
    ):
        # accept schema or pydantic schema
        self.kwargs = (
            kwargs  # NOTE: kwargs are set from self.gridschema.datagrid_traits below...
        )
        self.by_title = by_title
        self.selection_mode = MAP_TRANSPOSED_SELECTION_MODE[self.transposed]
        self.model, self.schema = asch._init_model_schema(schema, by_alias=by_alias, generate_pydantic_model_from_json_schema=generate_pydantic_model_from_json_schema)
        # ^ generates gridschema
        self.gridschema.get_traits = self.datagrid_trait_names
        _data = self._init_data(data)
        super().__init__(_data)
        {setattr(self, k, v) for k, v in self.gridschema.datagrid_traits.items()}
        # annoyingly have to add this due to renderers being overwritten...
        if "global_decimal_places" in self.gridschema.datagrid_traits.keys():
            self.global_decimal_places = self.gridschema.datagrid_traits[
                "global_decimal_places"
            ]
        assert isinstance(self.count_changes, int)
        # ^ this sets the default value and initiates trait change observer in `datagrid.py`
        if order is not None:
            self.order = order

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

    def get_default_data(self):
        if self.gridschema._get_default_data():
            data = pd.DataFrame(self.gridschema._get_default_data())
            if self.by_title:
                data = data.rename(columns=self.map_name_index)
        else:
            data = pd.DataFrame(
                self.gridschema._get_default_data(), columns=self.map_index_name
            )
        return data

    def _init_data(self, data) -> pd.DataFrame:
        if data is None:
            return self.gridschema.get_default_dataframe(
                order=self.order, transposed=self.transposed
            )
        else:
            return self.gridschema.coerce_data(
                data, order=self.order, transposed=self.transposed
            )

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
            self.set_cell_value(column_name, primary_key_value, new_value)
            return {
                "column_name": column_name,
                "primary_key_value": primary_key_value,
                "old_value": old,
                "new_value": new_value,
            }
        else:
            pass

    def set_item_value(self, index: int, value: dict):
        """
        set row (transposed==False) or col (transposed==True) value
        """
        if self.order is not None:
            value = {o: value[o] for o in self.order}
        if self.transposed:
            return self.set_col_value(index, value)
        else:
            return self.set_row_value(index, value)

    def _check_indexes(self, value: dict):
        """Check whether indexes of value are a subset of the schema

        Args:
            value (dict): The data we want to input into the row.
        """
        if set(value.keys()).issubset(set(self.map_name_index.keys())):
            return True
        else:
            return False

    def set_row_value(self, index: int, value: dict):
        """Set a chosen row using the index and a value given.

        Args:
            index (int): The key of the row. # TODO: is this defo an int?
            value (dict): The data we want to input into the row.
        """
        if self._check_indexes(value=value):
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
        """Set a chosen col using the index and a value given.

        Note: We do not call value setter to apply values as it resets the datagrid.

        Args:
            index (int): The index of the col
            value (dict): The data we want to input into the col.
        """
        column_name = self.get_col_name_from_index(index)
        if self._check_indexes(value=value):
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
    # these terms (below) avoid row or col terminology and can be used if transposed or not...
    # only these methods are called be EditGrid, allowing it to operate the same if the
    # view is transposed or not.
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
        return [
            self.apply_map_name_title(s._data["data"].loc[r].to_dict()) for r in rows
        ]

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
        return [s._data["data"].loc[r][index] for r in rows]

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
        """Return the dictionary of selected rows where index is row index. still works if transform applied."""
        if self.transposed:
            return self.data.T.loc[self.selected_col_indexes].to_dict("index")
        else:
            return self.data.loc[self.selected_row_indexes].to_dict("index")

    # ----------------


# -

if __name__ == "__main__":
    from IPython.display import display
    from pydantic import RootModel

    class DataFrameCols(BaseModel):
        string: str = Field(
            "string",
            title="Important String",
            column_width=120,
        )
        integer: int = Field(40, title="Integer of somesort", column_width=400)
        floater: float = Field(
            1.3398234, title="Floater", column_width=70  # , renderer={"format": ".2f"}
        )

    class TestDataFrame(RootModel):
        root: ty.List[DataFrameCols] = Field(
            json_schema_extra=dict(format="dataframe", global_decimal_places=2),
        )

    grid = AutoGrid(schema=TestDataFrame, by_title=True)
    display(grid)

if __name__ == "__main__":
    # ORDER OVERRIDE
    class DataFrameCols(BaseModel):
        string: str = Field(
            "string",
            title="Important String",
            json_schema_extra=dict(column_width=120),
        )
        integer: int = Field(
            40, title="Integer of somesort", json_schema_extra=dict(column_width=150)
        )
        floater: float = Field(
            1.3398234, title="Floater", json_schema_extra=dict(column_width=70)
        )

    class TestDataFrame(RootModel):
        root: ty.List[DataFrameCols] = Field(
            json_schema_extra=dict(format="dataframe", global_decimal_places=2),
        )

    grid = AutoGrid(
        schema=TestDataFrame,
        # transposed=True,
        order=(
            "floater",
            "string",
            # "integer",
        ),
    )
    display(grid)
    grid.data = grid._init_data(
        pd.DataFrame(
            [DataFrameCols(string="test", floater=2.45, integer=2).model_dump()]
        )
    )

# +
# grid.traits()
# -

if __name__ == "__main__":
    display(grid.selections)

if __name__ == "__main__":
    # ORDER OVERRIDE
    class DataFrameCols(BaseModel):
        string: str = Field(
            "string",
            title="Important String",
            json_schema_extra=dict(column_width=120),
        )
        integer: int = Field(
            40, title="Integer of somesort", json_schema_extra=dict(column_width=150)
        )
        floater: float = Field(
            1.3398234,
            title="Floater",
            json_schema_extra=dict(column_width=70),  # , renderer={"format": ".2f"}
        )

    class TestDataFrame(RootModel):
        root: ty.List[DataFrameCols] = Field(
            json_schema_extra=dict(format="dataframe", global_decimal_places=2),
        )

    grid = AutoGrid(schema=TestDataFrame, order=("floater", "string", "integer"))
    display(grid)

if __name__ == "__main__":

    class DataFrameCols(BaseModel):
        string: str = Field(
            title="Important String",
            column_width=120,
        )
        integer: int = Field(
            title="Integer of somesort", json_schema_extra=dict(column_width=400)
        )
        floater: float = Field(
            title="Floater",
            json_schema_extra=dict(column_width=70),  # , renderer={"format": ".2f"}
        )

    class TestDataFrame(RootModel):
        root: ty.List[DataFrameCols] = Field(
            [
                DataFrameCols(string="string", integer=1, floater=1.2),
                DataFrameCols(string="another string", integer=10, floater=2.5),
                DataFrameCols(string="test", integer=42, floater=0.78),
            ],
            json_schema_extra=dict(format="dataframe", global_decimal_places=2),
        )

    grid = AutoGrid(schema=TestDataFrame, by_title=True)
    display(grid)

# +
if __name__ == "__main__":
    grid.data = pd.DataFrame(grid.data.to_dict(orient="records") * 4)  # .T

if __name__ == "__main__":
    print(grid.is_transposed)
# -



# +
if __name__ == "__main__":
    grid.transposed = True

if __name__ == "__main__":
    grid.set_item_value(0, {"string": "check", "integer": 2, "floater": 3.0})

# +


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
    from pydantic import RootModel

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
            json_schema_extra=dict(
                column_width=70, section="b"
            ),  # , renderer={"format": ".2f"}
        )

    class TestDataFrame(RootModel):
        root: ty.List[DataFrameCols] = Field(
            [DataFrameCols()],
            json_schema_extra=dict(
                format="dataframe",
                global_decimal_places=2,
                datagrid_index_name=("section", "title"),
            ),
        )

    grid = AutoGrid(schema=TestDataFrame, by_title=True)
    display(grid)
# -

if __name__ == "__main__":
    grid.data = pd.DataFrame(grid.data.to_dict(orient="records") * 4)

if __name__ == "__main__":
    grid.transposed = True

if __name__ == "__main__":
    from pydantic import RootModel

    # Check hide_nan works
    class DataFrameCols(BaseModel):
        floater: float = Field(
            None,
        )
        inty: int = Field(
            None,
        )
        stringy: str = Field(
            None,
        )

    class TestDataFrame(RootModel):
        root: ty.List[DataFrameCols] = Field(
            json_schema_extra=dict(format="dataframe", hide_nan=True),
        )

    grid = AutoGrid(
        schema=TestDataFrame,
        data=pd.DataFrame(
            [
                DataFrameCols(inty=3, stringy="string").dict(),
                DataFrameCols(floater=2.555).dict(),
            ]
        ),
    )
    display(grid)
