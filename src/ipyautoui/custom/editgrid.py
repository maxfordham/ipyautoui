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
"""General widget for editing data"""
# %run __init__.py
# %run ../__init__.py
# %load_ext lab_black
import traitlets as tr
import typing as ty
import collections
import traceback
import functools

import immutables
import pandas as pd
import ipywidgets as widgets
from typing import List
from markdown import markdown
from pydantic import BaseModel, Field
from ipydatagrid import CellRenderer, DataGrid, TextRenderer
from ipydatagrid.datagrid import SelectionHelper


import ipyautoui.autoipywidget as aui
import ipyautoui.custom.save_buttonbar as sb
from ipyautoui._utils import obj_from_importstr
from ipyautoui.automapschema import attach_schema_refs

# from ipyautoui.autoipywidget import AutoIpywidget


frozenmap = immutables.Map

# TODO: Tasks pending completion -@jovyan at 9/14/2022, 5:09:18 PM
#       review how ipydatagrid works. it has a _data trait which has
#       a schema. Perhaps we can make better use of this / contribute
#       back to the main repo.

# BUG: Reported defects -@jovyan at 9/16/2022, 5:25:13 PM
#      the selection when filtered issue is creating a problem.

# TODO: Tasks pending completion -@jovyan at 9/22/2022, 9:25:53 PM
#       Can BaseForm inherit autoipywidget.AutoObject directly?

# TODO: give ButtonBar its own module

# TODO: rename "add" to "fn_add" so not ambiguous...


# +
# TODO: Move to utils
def is_incremental(li):
    return li == list(range(li[0], li[0] + len(li)))


def get_grid_column_properties_from_schema(schema):
    return schema["items"]["properties"]


def get_name_title_map_from_schema_properties(properties):
    return {k: v["title"] for k, v in properties.items()}


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

    Returns:
        list: list of dictionary column values
    """
    di = {}
    for k, v in properties.items():
        if "default" in v.keys():
            di[k] = v["default"]
        else:
            di[k] = property_types[k]
    return di


def get_default_row_data_from_schema_root(schema):
    if "default" in schema.keys():
        return schema["default"]
    else:
        return None


def get_column_widths_from_schema(schema, column_properties, map_name_title, **kwargs):
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
        _ = {map_name_title[k]: v for k, v in kwargs["column_widths"].items()}
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
    schema, column_properties, map_name_title, **kwargs
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
        _ = {map_name_title[k]: v for k, v in kwargs["renderers"].items()}
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


def try_getattr(obj, name):
    try:
        return getattr(obj, name)
    except:
        pass


class GridSchema:
    def __init__(self, schema, get_traits=None, **kwargs):
        self.schema = schema
        self.get_traits = get_traits
        self.map_name_title = get_name_title_map_from_schema_properties(self.properties)
        self.map_title_name = {v: k for k, v in self.map_name_title.items()}
        {
            setattr(self, k, v)
            for k, v in get_global_renderers_from_schema(self.schema, **kwargs)
        }
        # ^ sets: ["default_renderer", "header_renderer", "corner_renderer"]
        self.renderers = get_column_renderers_from_schema(
            schema,
            column_properties=self.properties,
            map_name_title=self.map_name_title,
            **kwargs,
        )
        if len(self.renderers) == 0:
            self.renderers = None
        self.column_widths = get_column_widths_from_schema(
            schema, self.properties, self.map_name_title, **kwargs
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
    def datagrid_traits(self) -> dict[str, ty.Any]:
        if self.get_traits is None:
            return {}
        else:
            _ = {t: try_getattr(self, t) for t in self.get_traits}
            return {k: v for k, v in _.items() if v is not None}

    def _get_default_data(self):
        return get_default_row_data_from_schema_root(self.schema)

    def _get_default_row(self):
        row = get_default_row_data_from_schema_properties(
            self.properties, self.column_property_types
        )
        if self.default_data is not None:
            if len(self.default_data) == 1:
                return self.default_data[0]
            else:
                return row
        else:
            self.default_data = [row]
            return row

    @property
    def properties(self):
        return get_grid_column_properties_from_schema(self.schema)


# -


class DataGrid(DataGrid):
    """extends DataGrid with useful generic functions"""

    global_decimal_places = tr.Int(default_value=None, allow_none=True)

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


class AutoGrid(DataGrid):
    """a thin wrapper around DataGrid that makes makes it possible to initiate the
    grid from a json-schema / pydantic model.

    Traits that can be set in a DataGrid instance can be reviewed using gr.traits().
    Note that of these traits, `column_widths` and `renderers` have the format
    {'column_name': <setting>}.

    """

    # _value = tr.List()
    schema = tr.Dict()

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

    def __init__(
        self,
        schema: ty.Union[dict, ty.Type[BaseModel]],
        data: ty.Optional[pd.DataFrame] = None,
        by_alias: bool = False,
        by_title: bool = True,
        **kwargs,
    ):
        # accept schema or pydantic schema
        self.kwargs = kwargs
        self.by_title = by_title

        self.model, self.schema = aui._init_model_schema(schema, by_alias=by_alias)
        data = self._init_data(data)
        super().__init__(data)
        self.gridschema.get_traits = self.datagrid_trait_names
        {setattr(self, k, v) for k, v in self.gridschema.datagrid_traits.items()}

        # annoyingly have to add this due to renderers being overwritten...
        if "global_decimal_places" in self.gridschema.datagrid_traits.keys():
            self.global_decimal_places = self.gridschema.datagrid_traits[
                "global_decimal_places"
            ]

    def records(self, keys_as_title=False):
        if keys_as_title:
            return self.data.to_dict(orient="records")
        else:
            return self.data.rename(columns=self.map_title_name).to_dict(
                orient="records"
            )

    @property
    def default_row(self):
        return self.gridschema.default_row

    @property
    def datagrid_trait_names(self):
        return [l for l in self.trait_names() if l[0] != "_" and l != "schema"]

    @property
    def properties(self):
        return self.gridschema.properties

    @property
    def map_name_title(self):
        return self.gridschema.map_name_title

    @property
    def map_title_name(self):
        return self.gridschema.map_title_name

    def get_default_data(self):
        data = pd.DataFrame(self.gridschema.default_data)
        if self.by_title:
            data = data.rename(columns=self.map_name_title)
        return data

    def map_titles_to_data(self, data):
        if set(data.columns) == set(self.map_name_title.keys()):
            return data.rename(columns=self.map_name_title)
        elif set(data.columns) == set(self.map_name_title.values()):
            return data
        else:
            raise ValueError("input data does not match specified schema")

    def _init_data(self, data) -> pd.DataFrame:
        if data is None:
            return self.get_default_data()
        else:
            return self.map_titles_to_data(data)

    def set_row_value(self, key: int, value: dict):
        """Set a chosen row using the key and a value given.

        Note: We do not call value setter to apply values as it resets the datagrid.

        Args:
            key (int): The key of the row.
            value (dict): The data we want to input into the row.
        """
        if set(value.keys()) == set(self.map_name_title.keys()):
            # value_with_titles is used for datagrid
            value = {self.map_name_title.get(name): v for name, v in value.items()}
        elif set(value.keys()) == set(self.map_name_title.values()):
            pass
        else:
            raise Exception("Columns of value given do not match with value keys.")
        for column, v in value.items():
            self.set_cell_value(column, key, v)

        # self._value[key] = {k: v for k, v in value.items()}

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

    # move rows around
    # ----------------
    def _swap_rows(self, key_a: int, key_b: int):  # TODO: fix!
        """Swap two rows by giving their keys.

        Args:
            key_a (int): Key of a row.
            key_b (int): Key of another row.
        """
        di_a = self.value[key_a]
        di_b = self.value[key_b]
        self.set_row_value(key=key_b, value=di_a)
        self.set_row_value(key=key_a, value=di_b)

    def _move_row_down(self, key: int):
        """Move a row down.

        Args:
            key (int): Key of the row
        """
        if key + 1 == len(self.data):
            raise Exception("Can't move down last row.")
        self._swap_rows(key_a=key, key_b=key + 1)

    def _move_row_up(self, key: int):
        """Move a row up.

        Args:
            key (int): Key of the row
        """
        if key - 1 == -1:
            raise Exception("Can't move up first row.")
        self._swap_rows(key_a=key, key_b=key - 1)

    def _move_rows_up(self, li_keys: List[int]):
        """Move multiple rows up.

        Args:
            li_key (List[int]): List of row keys.
        """
        if is_incremental(sorted(li_keys)) is False:
            raise Exception("Only select a property or block of properties.")
        for key in sorted(li_keys):
            self._move_row_up(key)
        self.selections = [
            {"r1": min(li_keys) - 1, "r2": max(li_keys) - 1, "c1": 0, "c2": 2}
        ]

    def _move_rows_down(self, li_keys: List[int]):
        """Move multiple rows down.

        Args:
            li_key (List[int]): List of row keys.
        """
        if is_incremental(sorted(li_keys)) is False:
            raise Exception("Only select a property or block of properties.")
        for key in sorted(li_keys, reverse=True):
            self._move_row_down(key)
        self.selections = [
            {"r1": min(li_keys) + 1, "r2": max(li_keys) + 1, "c1": 0, "c2": 2}
        ]

    # ----------------
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

    def apply_map_name_title(self, row_data):
        return {
            self.map_title_name[k]: v
            for k, v in row_data.items()
            if k in self.map_title_name.keys()
        }

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
    def selected_key(self) -> ty.Any:
        try:
            return self.selected_keys[0]
        except:
            return None

    @property
    def selected_keys(self):
        """Return the keys of the selected rows. still works if transform applied."""
        s = self.selected_visible_cell_iterator
        index = self.get_dataframe_index(self.data)
        rows = set([l["r"] for l in s])
        return [s._data["data"][r][index] for r in rows]

    # ----------------


# +
# grid.map_title_name
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

    # schema = attach_schema_refs(TestDataFrame.schema())["properties"]["dataframe"]

    grid = AutoGrid(schema=TestDataFrame)
    display(grid)


if __name__ == "__main__":
    eg_value = [
        {
            "string": "important string",
            "integer": 1,
            "floater": 3.14,
        },
        {
            "string": "update",
            "integer": 4,
            "floater": 3.12344,
        },
        {"string": "evening", "integer": 5, "floater": 3.14},
        {"string": "morning", "integer": 5, "floater": 3.14},
        {"string": "number", "integer": 3, "floater": 3.14},
    ]
    grid.data = pd.DataFrame(eg_value * 10)


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


class EditGrid(widgets.VBox):
    _value = tr.List()

    @property
    def value(self):
        self._value = self.grid.records()
        # _value trait updated called every time the data is retrieved...
        # probs not the best way in the long run... need to add watcher...
        return self._value

    @value.setter
    def value(self, value):
        if value == [] or value is None:
            self.grid.data = self.grid.get_default_data()
        else:
            df = pd.DataFrame(value)
            self.grid.data = self.grid.map_titles_to_data(df)
        self._value = self.grid.records()

    def __init__(
        self,
        schema: ty.Union[dict, ty.Type[BaseModel]],
        value: ty.Optional[dict] = None,
        by_alias: bool = False,
        by_title: bool = True,
        datahandler: ty.Optional[DataHandler] = None,
        ui_add: ty.Optional[ty.Callable] = None,
        ui_edit: ty.Optional[ty.Callable] = None,
        description: str = "",
        fn_on_copy: ty.Callable = None,  # TODO: don't think this is required...
    ):
        self.description = widgets.HTML(description)
        self.by_title = by_title
        self.fn_on_copy = fn_on_copy
        self.by_alias = by_alias
        # self.model, self.schema = aui._init_model_schema(schema, by_alias=by_alias)
        self.datahandler = datahandler
        self.grid = AutoGrid(
            schema, value=value, selection_mode="row", by_alias=self.by_alias
        )
        set_cls_editable_row = (
            lambda v: functools.partial(aui.AutoObject, self.row_schema)
            if v is None
            else functools.partial(v, self.row_schema)
        )
        self.ui_add = set_cls_editable_row(ui_add)()  # widgets.Box()  #
        self.ui_edit = set_cls_editable_row(ui_edit)()  # widgets.Box()  #
        self._init_form()
        self.

    def _init_row_controls(self):
        self.ui_edit.show_savebuttonbar = True
        self.ui_edit.savebuttonbar.fns_onsave = [self._save_edit_to_grid, self._patch]
        self.ui_edit.savebuttonbar.fns_onrevert = [self._set_ui_edit_to_selected_row]
        self.ui_add.show_savebuttonbar = True
        self.ui_add.savebuttonbar.fns_onsave = [self._save_add_to_grid, self._post]
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
        self.buttonbar_grid = sb.ButtonBar(
            add=self._add,
            edit=self._edit,
            copy=self._copy,
            delete=self._delete,
            backward=self.setview_default,
            show_message=False,
            # layout=widgets.Layout(padding="0px 0px 40px 0px"),
        )
        # self.buttonbar_row = sb.SaveButtonBar()
        self.addrow = widgets.VBox()
        self.editrow = widgets.VBox()
        self.children = [
            self.description,
            self.buttonbar_grid,
            # self.buttonbar_row,
            self.ui_add,
            self.ui_edit,
            self.grid,
        ]
        self.setview_default()
        self._init_controls()

    def _init_controls(self):
        self.grid.observe(self._observe_selections, "selections")

    def _observe_selections(self, onchange):
        if self.buttonbar_grid.edit.value:
            self._set_ui_edit_to_selected_row()

    def setview_add(self):
        # self.buttonbar_row.layout.display = ""
        self.ui_add.layout.display = ""

    def setview_edit(self):
        # self.buttonbar_row.layout.display = ""
        self.ui_edit.layout.display = ""

    def setview_default(self):
        # self.buttonbar_row.layout.display = "None"
        self.ui_edit.layout.display = "None"
        self.ui_add.layout.display = "None"
        self.buttonbar_grid.add.value = False
        self.buttonbar_grid.edit.value = False

    def _check_one_row_selected(self):
        if len(self.grid.selected_keys) > 1:
            raise Exception(
                markdown("  👇 _Please only select ONLY one row from the table!_")
            )

    # edit row
    # --------------------------------------------------------------------------
    def _validate_edit_click(self):
        if len(self.grid.selected_keys) == 0:
            raise ValueError("you must select a row")
        self._check_one_row_selected()

    def _save_edit_to_grid(self):
        self.grid.set_row_value(self.grid.selected_key, self.ui_edit.value)
        self.setview_default()

    def _set_ui_edit_to_selected_row(self):
        self.ui_edit.value = self.grid.selected_row

    def _patch(self):
        if self.datahandler is not None:
            self.datahandler.fn_patch(self.ui_edit.value)

    def _edit(self):
        try:
            self._validate_edit_click()
            self._set_ui_edit_to_selected_row()
            # self.buttonbar_row.fns_onsave = [self._save_edit_to_grid, self._patch]
            # self.buttonbar_row.fns_onrevert = self._set_ui_edit_to_selected_row
            self.buttonbar_grid.message.value = markdown("  ✏️ _Editing Value_ ")
            self.setview_edit()

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
            self.value = [self.ui_add.value]
        else:
            # Append new row onto data frame and set to grid's data.
            value = self.value
            value.append(self.ui_add.value)
            self.value = value  # Call setter
        self.setview_default()

    def _set_ui_add_to_default_row(self):
        if self.ui_add.value == self.grid.default_row:
            self.ui_add.savebuttonbar.unsaved_changes = False
        else:
            self.ui_add.savebuttonbar.unsaved_changes = True

    def _post(self):
        if self.datahandler is not None:
            self.datahandler.fn_post(self.ui_add.value)

    def _add(self):
        try:
            self._set_ui_add_to_default_row()
            # self.buttonbar_row.fns_onsave = [self._save_add_to_grid, self._post]
            # self.buttonbar_row.fns_onrevert = [self._set_ui_add_to_default_row]
            self.buttonbar_grid.message.value = markdown("  ✏️ _Editing Value_ ")
            self.setview_add()

        except Exception as e:
            self.buttonbar_grid.edit.value = False
            self.buttonbar_grid.message.value = markdown(
                "  👇 _Please select one row from the table!_ "
            )
            traceback.print_exc()

    # --------------------------------------------------------------------------

    # copy
    # --------------------------------------------------------------------------
    def _copy(self):
        try:
            if self.grid.selected_keys == []:
                self.buttonbar_grid.message.value = markdown(
                    "  👇 _Please select a row from the table!_ "
                )
            else:
                li_values_selected = [
                    self.value[i] for i in sorted([i for i in self.grid.selected_keys])
                ]
                if self.fn_on_copy is not None:
                    li_values_selected = self.fn_on_copy(li_values_selected)
                if self.datahandler is not None:
                    for value in li_values_selected:
                        self.datahandler.fn_copy(value)
                    self._reload_all_data()
                else:
                    self.value += li_values_selected
                    # ^ add copied values

                self.buttonbar_grid.message.value = markdown("  📝 _Copied Data_ ")
                self._edit_bool = False  # Want to add the values
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

    def _set_toggle_buttons_to_false(self):
        if self.buttonbar_grid.add.value is True:
            self.buttonbar_grid.add.value = False
        elif self.buttonbar_grid.edit.value is True:
            self.buttonbar_grid.edit.value = False

    def _delete(self):
        try:
            self._set_toggle_buttons_to_false()  # TODO: a an "are you sure?" dialogue...
            if self.grid.selected_keys:
                print(f"Row Number: {self.grid.selected_keys}")
                if self.datahandler is not None:
                    value = [self.value[i] for i in self.grid.selected_keys]
                    for v in value:
                        self.datahandler.fn_delete(v)
                    self._reload_all_data()
                else:
                    self.value = [
                        value
                        for i, value in enumerate(self.value)
                        if i not in self.grid.selected_keys
                    ]
                    # ^ Only set for values NOT in self.grid.selected_keys
                self.buttonbar_grid.message.value = markdown("  🗑️ _Deleted Row_ ")

            else:
                self.buttonbar_grid.message.value = markdown(
                    "  👇 _Please select one row from the table!_"
                )
        except Exception as e:
            traceback.print_exc()


if __name__ == "__main__":
    AUTO_GRID_DEFAULT_VALUE = [
        {
            "string": "important string",
            "integer": 1,
            "floater": 3.14,
        },
        {
            "string": "update",
            "integer": 4,
            "floater": 3.12344,
        },
        {"string": "evening", "integer": 5, "floater": 3.14},
        {"string": "morning", "integer": 5, "floater": 3.14},
        {"string": "number", "integer": 3, "floater": 3.14},
    ]

    class DataFrameCols(BaseModel):
        string: str = Field("string", column_width=100)
        integer: int = Field(1, column_width=80)
        floater: float = Field(3.1415, column_width=70, aui_sig_fig=3)

    class TestDataFrameOnly(BaseModel):
        """a description of TestDataFrame"""

        __root__: ty.List[DataFrameCols] = Field(
            default=AUTO_GRID_DEFAULT_VALUE, format="dataframe"
        )

    description = markdown(
        "<b>The Wonderful Edit Grid Application</b><br>Useful for all editing purposes"
        " whatever they may be 👍"
    )
    editgrid = EditGrid(
        schema=TestDataFrameOnly, description=description, ui_add=None, ui_edit=AutoUi
    )
    display(editgrid)

# +
# editgrid.ui_add.show_savebuttonbar = True

# +
# editgrid.grid.selected_keys == []
# -

if __name__ == "__main__":

    class TestDataFrame(BaseModel):
        __root__: ty.List[DataFrameCols] = Field(
            default=AUTO_GRID_DEFAULT_VALUE, format="dataframe"
        )


if __name__ == "__main__":
    from ipyautoui import AutoUi
    from ipyautoui.autoipywidget import AutoIpywidget

    ui = AutoIpywidget(schema=TestDataFrame)
    display(ui)

if __name__ == "__main__":
    description = markdown(
        "<b>The Wonderful Edit Grid Application</b><br>Useful for all editing purposes"
        " whatever they may be 👍"
    )
    editgrid = EditGrid(
        schema=TestDataFrame, description=description, ui_add=None, ui_edit=AutoUi
    )
    editgrid.value = AUTO_GRID_DEFAULT_VALUE

    display(editgrid)
