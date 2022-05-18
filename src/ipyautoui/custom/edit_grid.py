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
#       jupytext_version: 1.13.8
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

import sys
import pathlib
import json
import requests
import traitlets
import functools
import typing
import collections
from copy import deepcopy

import immutables
import pandas as pd
import ipywidgets as widgets
from markdown import markdown
from ipydatagrid import DataGrid, TextRenderer, BarRenderer, Expr, VegaExpr
from pydantic import BaseModel, Field
from ipyautoui._utils import obj_from_string, display_pydantic_json, round_sig_figs
from ipyautoui.automapschema import attach_schema_refs
from ipyautoui.autoipywidget import AutoIpywidget

# from ipyautoui.displayfile import AutoDisplay
from ipyautoui import AutoUi

from ipyautoui.constants import (
    BUTTON_WIDTH_MIN,
    TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT,
    KWARGS_DATAGRID_DEFAULT,
)
from ipyautoui.custom import SaveButtonBar

frozenmap = immutables.Map


# -


class BaseForm(widgets.VBox, traitlets.HasTraits):

    _value = traitlets.Dict()

    def __init__(
        self,
        save: typing.Callable,
        revert: typing.Callable,
        schema: dict,
        value: dict = None,
        fn_onsave: typing.Callable = lambda: None,
    ):
        self.fn_save = save
        self.fn_revert = revert
        self.fn_onsave = fn_onsave
        self.model, schema = self._init_model_schema(schema)
        self.out = widgets.Output()
        self._init_form(schema)
        self._init_controls()

    def _init_model_schema(self, schema):
        if type(schema) == dict:
            model = None  # jsonschema_to_pydantic(schema)  # TODO: do this!
        else:
            model = schema  # the "model" passed is a pydantic model
            schema = model.schema()
        return model, schema

    def _init_form(self, schema):
        super().__init__()  # main container
        self.autowidget = AutoIpywidget(schema=schema)
        self.save_button_bar = SaveButtonBar(
            save=self.fn_save, revert=self.fn_revert, fn_onsave=self.fn_onsave
        )
        self.title = widgets.HTML()
        self.children = [self.title, self.save_button_bar, self.autowidget]
        self.save_button_bar._unsaved_changes(False)
        self.value = self.autowidget.value

    def _init_controls(self):
        self.autowidget.observe(self._watch_change, "_value")

    def _watch_change(self, change):
        self.save_button_bar._unsaved_changes(True)


if __name__ == "__main__":

    class TestModel(BaseModel):
        string: str = Field("string", title="Important String")
        integer: int = Field(40, title="Integer of somesort")
        floater: float = Field(1.33, title="floater")

    def test_save():
        print("Saved.")

    def test_revert():
        print("Reverted.")

    baseform = BaseForm(schema=TestModel.schema(), save=test_save, revert=test_revert)
    display(baseform)

if __name__ == "__main__":
    # With nested object

    class DataFrameCols(BaseModel):
        string: str = Field("string", aui_column_width=100)
        integer: int = Field(1, aui_column_width=80)
        floater: float = Field(3.1415, aui_column_width=70, aui_sig_fig=3)
        something_else: float = Field(324, aui_column_width=100)

    class TestDataFrame(BaseModel):
        dataframe: typing.List[DataFrameCols] = Field(..., format="dataframe")

    schema = attach_schema_refs(TestDataFrame.schema())["properties"]["dataframe"][
        "items"
    ]
    baseform = BaseForm(schema=schema, save=test_save, revert=test_revert)
    display(baseform)

if __name__ == "__main__":
    di = {"string": "update", "integer": 10, "floater": 3.123, "something_else": 444}
    baseform.autowidget.value = di


class ButtonBar(widgets.HBox):
    def __init__(
        self,
        add: typing.Callable,
        edit: typing.Callable,
        copy: typing.Callable,
        delete: typing.Callable,
        backward: typing.Callable,
        show_message: bool = True,
    ):
        self.show_message = show_message
        self.fn_add = add
        self.fn_edit = edit
        self.fn_copy = copy
        self.fn_delete = delete
        self.fn_backward = backward
        self.out = widgets.Output()
        self._init_form()
        self._init_controls()

    def _init_form(self):
        super().__init__()  # main container
        self.add = widgets.ToggleButton(
            icon="plus",
            button_style="success",
            style={"font_weight": "bold"},
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.edit = widgets.ToggleButton(
            icon="edit",
            button_style="warning",
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.copy = widgets.Button(
            icon="copy",
            button_style="primary",
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.delete = widgets.Button(
            icon="trash-alt",
            button_style="danger",
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.message = widgets.HTML()
        children = [self.add, self.edit, self.copy, self.delete]
        children.append(self.message)
        self.children = children

    def _init_controls(self):
        self.add.observe(self._add, "value")
        self.edit.observe(self._edit, "value")
        self.copy.on_click(self._copy)
        self.delete.on_click(self._delete)

    def _add(self, onchange):
        self._reset_message()
        if self.add.value:
            if self.edit.value:
                self.edit.value = False  # If Edit button already clicked on and add is then clicked on then, trigger toggle for Edit button.
            self.add.tooltip = "Go back to table"
            self.add.layout.border = TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT
            self.fn_add()
            if self.show_message:
                self.message.value = markdown("  ➕ _Adding Value_ ")
        else:
            self._reset_message()
            self.add.tooltip = "Add"
            self.add.layout.border = None
            self.add.icon = "plus"
            self.add.button_style = "success"
            self.fn_backward()

    def _edit(self, onchange):
        self._reset_message()
        if self.edit.value:
            if self.add.value:
                self.add.value = False
            self.edit.tooltip = "Go back to table"
            self.edit.layout.border = TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT
            self.fn_edit()
            if self.show_message:
                self.message.value = markdown("  ✏️ _Editing Value_ ")
        else:
            self._reset_message()
            self.edit.tooltip = "Edit"
            self.edit.layout.border = None
            self.edit.icon = "edit"
            self.edit.button_style = "warning"
            self.fn_backward()

    def _copy(self, onchange):
        self._reset_message()
        self.fn_copy()
        if self.show_message:
            self.message.value = markdown("  📝 _Copying Value_ ")

    def _delete(self, click):
        self._reset_message()
        self.fn_delete()
        if self.show_message:
            self.message.value = markdown("  🗑️ _Deleting Value_ ")

    def _reset_message(self):
        self.message.value = ""  # Reset message


if __name__ == "__main__":

    def add():
        print("ADD")

    def edit():
        print("EDIT")

    def copy():
        print("COPY")

    def delete():
        print("DELETE")

    def backward():
        print("BACK")

    button_bar = ButtonBar(
        add=add, edit=edit, copy=copy, delete=delete, backward=backward,
    )

    display(button_bar)


class GridWrapper(DataGrid):
    def __init__(
        self,
        schema: dict,
        value: dict = None,
        kwargs_datagrid_default: frozenmap = frozenmap(),
        kwargs_datagrid_update: frozenmap = frozenmap(),
        ignore_cols: list = [],
    ):
        # accept schema or pydantic schema
        self.model, schema = self._init_model_schema(schema)
        self.di_cols_properties = schema[
            "properties"
        ]  # Obtain each column's properties

        # Put all objects in datagrid belonging to that particular model
        if value is None:
            li_default_value = [
                {
                    col_name: (
                        col_data["default"] if "default" in col_data.keys() else None
                    )
                    for col_name, col_data in self.di_cols_properties.items()
                }
            ]  # default value
            df = pd.DataFrame.from_dict(li_default_value)

        else:
            df = pd.DataFrame.from_dict([val.dict() for val in value])

        self._check_data(df, ignore_cols)  # Checking data frame

        self.kwargs_datagrid_default = kwargs_datagrid_default
        self._init_form(df)
        self.kwargs_datagrid_update = kwargs_datagrid_update

    def _init_model_schema(self, schema):
        if type(schema) == dict:
            model = None  # jsonschema_to_pydantic(schema)  # TODO: do this!
        else:
            model = schema  # the "model" passed is a pydantic model
            schema = model.schema()
        return model, schema

    def _init_form(self, df):
        super().__init__(
            df,
            selection_mode="row",
            renderers=self.datetime_format_renderers,
            **self.kwargs_datagrid_default,
        )  # main container
        if self.aui_column_widths:
            self._set_column_widths()
        if self.aui_sig_figs and self.data.empty is False:
            self._round_sig_figs()  # Rounds any specified fields in schema

    @property
    def kwargs_datagrid_update(self):
        return self._kwargs_datagrid_update

    @kwargs_datagrid_update.setter
    def kwargs_datagrid_update(self, value):
        self._kwargs_datagrid_update = value
        for k, v in value.items():
            setattr(self, k, v)

    @property
    def selected_rows(self):
        return [{"r1": v["r1"], "r2": v["r2"]} for v in self.selections]

    @property
    def selected_obj_id(self):
        return self.selected_cell_values[
            -1
        ]  # Set to -1 as this as ID is last column. Will break if ID moves column!

    @property
    def aui_sig_figs(self):
        self._aui_sig_figs = {
            col_name: col_data["aui_sig_fig"]
            for col_name, col_data in self.di_cols_properties.items()
            if "aui_sig_fig" in col_data
        }
        return self._aui_sig_figs

    @property
    def aui_column_widths(self):
        self._aui_column_widths = {
            col_name: col_data["aui_column_width"]
            for col_name, col_data in self.di_cols_properties.items()
            if "aui_column_width" in col_data
        }  # Obtaining column widths from schema object
        return self._aui_column_widths

    @property
    def datetime_format_renderers(self):
        date_time_fields = {
            col_name: col_data["format"]
            for col_name, col_data in self.di_cols_properties.items()
            if "format" in col_data
        }
        text_renderer_date_time_format = TextRenderer(
            format="%Y-%m-%d %H:%M:%S", format_type="time",
        )
        return {k: text_renderer_date_time_format for k, v in date_time_fields.items()}

    @property
    def column_names(self):
        return [col_name for col_name, col_data in self.di_cols_properties.items()]

    def _round_sig_figs(self):
        df = self.data
        for k, v in self.aui_sig_figs.items():
            df.loc[:, k] = df.loc[:, k].apply(lambda x: round_sig_figs(x, sig_figs=v))
        self.data = df  # Update data through setter

    def _set_column_widths(self):
        self.column_widths = self.aui_column_widths  # Set column widths for data grid.

    def _check_data(self, df, ignore_cols):
        """Checking column names in produced data frame match those within the schema."""
        columns = [column for column in df.columns if column not in ignore_cols]
        if not collections.Counter(columns) == collections.Counter(self.column_names):
            raise Exception(
                f"Schema fields and data fields do not match.\nRejected Columns: {list(set(columns).difference(self.column_names))}"
            )

    @property
    def selected_rows_(self):
        self._selected_rows_ = set()
        for di in self.selected_rows:
            r1 = di["r1"]
            r2 = di["r2"]
            if r1 == r2:
                self._selected_rows_.add(r1)
            else:
                for i in range(r1, r2 + 1):
                    self._selected_rows_.add(i)
        return self._selected_rows_


if __name__ == "__main__":

    class DataFrameCols(BaseModel):
        string: str = Field("string", aui_column_width=100)
        integer: int = Field(1, aui_column_width=80)
        floater: float = Field(3.1415, aui_column_width=70, aui_sig_fig=3)
        something_else: float = Field(324, aui_column_width=100)

    class TestDataFrame(BaseModel):
        dataframe: typing.List[DataFrameCols] = Field(..., format="dataframe")

    schema = attach_schema_refs(TestDataFrame.schema())["properties"]["dataframe"][
        "items"
    ]

    grid = GridWrapper(schema=schema)
    display(grid)

if __name__ == "__main__":
    value = [
        DataFrameCols(),
        DataFrameCols(floater=2131),
        DataFrameCols(floater=4123),
        DataFrameCols(floater=234),
    ]
    grid = GridWrapper(schema=schema, value=value)
    display(grid)


class DataHandler:  # Need BaseModel?
    fn_get_all_data: typing.Callable
    fn_post: typing.Callable
    fn_patch: typing.Callable
    fn_delete: typing.Callable


class EditGrid(widgets.VBox, traitlets.HasTraits):

    _value = traitlets.List()

    def __init__(
        self,
        schema: dict,
        value: dict = None,
        data_handler: typing.Type[BaseModel] = None,
        kwargs_datagrid_default: frozenmap = {},
        kwargs_datagrid_update: frozenmap = {},
        ignore_cols: list = [],
    ):
        self.model, self.schema = self._init_model_schema(
            schema
        )  # TODO: Will update to use model in the future
        self.data_handler = data_handler
        if self.data_handler is not None:
            df = pd.DataFrame(self.data_handler.fn_get_all_data(self))
        self.out = widgets.Output()
        self._init_form(
            value=value,
            schema=schema,
            kwargs_datagrid_default=kwargs_datagrid_default,
            kwargs_datagrid_update=kwargs_datagrid_update,
            ignore_cols=ignore_cols,
        )
        self._init_controls()
        self._edit_bool = False  # Initially define edit mode to be false

    def _init_model_schema(self, schema):
        if type(schema) == dict:
            model = None  # jsonschema_to_pydantic(schema)  # TODO: do this!
        else:
            model = schema  # the "model" passed is a pydantic model
            schema = model.schema()
        return model, schema

    def _init_form(
        self,
        schema,
        value,
        kwargs_datagrid_default,
        kwargs_datagrid_update,
        ignore_cols,
    ):
        super().__init__()  # main container
        self.button_bar = ButtonBar(
            add=self._add,
            edit=self._edit,
            copy=self._copy,
            delete=self._delete,
            backward=self._backward,
            show_message=False,
        )
        self.grid = GridWrapper(
            schema=schema,
            value=value,
            kwargs_datagrid_default=kwargs_datagrid_default,
            kwargs_datagrid_update=kwargs_datagrid_update,
            ignore_cols=ignore_cols,
        )
        self.baseform = BaseForm(
            schema=schema, save=self._save, revert=self._revert, fn_onsave=self._onsave,
        )
        self.baseform.title.value = ""
        self.button_bar.layout = widgets.Layout(padding="0px 20px")
        self.baseform.save_button_bar.layout = widgets.Layout(padding="0px 20px")
        self.baseform.layout = widgets.Layout(padding="0px 0px 40px 0px")
        self.children = [self.button_bar, self.baseform, self.grid]
        self.baseform.layout.display = "none"  # Hide base form menu

    def _init_controls(self):
        self.grid.observe(self._update_baseform, "selections")

    def _update_baseform(self, onchange):
        self.baseform.save_button_bar._unsaved_changes(False)
        if self.baseform.layout.display == "block":
            self.baseform.autowidget.value = self.di_row

    @property
    def data(self):
        return self.grid.data

    @data.setter
    def data(self, value):
        self.grid.data = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is not None:
            self._value = value
        self._set_value()

    @property
    def di_row(self):
        try:
            self._check_one_row_selected()  # Performing checks to see if only one row is selected
            self.selected_row = self.grid.selected_rows[0][
                "r1"
            ]  # Only one row selected during editing
            di_obj = self.grid.data.to_dict(orient="records")[
                self.selected_row
            ]  # obtaining object selected to put into base form
            return di_obj
        except Exception as e:
            self.button_bar.message.value = markdown(f"_{e}_")

    def _add(self):
        try:
            self._edit_bool = False  # Editing mode is False, therefore addition mode
            self.grid.clear_selection()  # Clear selection of data grid. We don't want to replace an existing value by accident.
            di_default_value = {
                col_name: col_data["default"]
                for col_name, col_data in self.schema["properties"].items()
            }
            self.initial_value = di_default_value
            self.baseform.autowidget.value = di_default_value
            self._display_baseform()
            self.button_bar.message.value = markdown("  ➕ _Adding Value_ ")
        except Exception as e:
            self.button_bar.message.value = markdown("  ☠️ _Failed to add_")

    def _edit(self):
        try:
            self._check_one_row_selected()
            di_obj = self.di_row
            self.initial_value = di_obj
            self.baseform.autowidget.value = di_obj  # Set values in fields
            self._display_baseform()
            self.button_bar.message.value = markdown("  ✏️ _Editing Value_ ")
            self._edit_bool = True  # Editing mode is True
        except Exception as e:
            self.button_bar.edit.value = False
            self.button_bar.message.value = markdown(
                "  👇 _Please select one row from the table!_ "
            )

    def _copy(self):
        try:
            selected_rows = self.grid.selected_rows_
            if selected_rows == set():
                self.button_bar.message.value = markdown(
                    "  👇 _Please select a row from the table!_ "
                )
            else:
                li_objs = [
                    self.data.to_dict(orient="records")[i]
                    for i in sorted([i for i in selected_rows])
                ]
                df_objs = pd.DataFrame(li_objs)

                if self.data_handler is not None:
                    self.data_handler.fn_post(self)
                else:
                    # Concat new row with existing grid data
                    self.grid.data = pd.concat(
                        [self.grid.data, df_objs], ignore_index=True
                    )

                self.button_bar.message.value = markdown("  📝 _Copied Data_ ")
                self._edit_bool = False  # Want to add the values
        except Exception as e:
            self.button_bar.message.value = markdown(
                "  👇 _Please select a row from the table!_ "
            )

    def _delete(self):
        try:
            self._set_toggle_buttons_to_false()
            # Delete from data frame.
            self.rows_to_delete = []
            if self.grid.selected_rows:
                for i in self.grid.selected_rows:
                    start_row = i["r1"]
                    end_row = i["r2"]
                    self.rows_to_delete += [i for i in range(*[start_row, end_row + 1])]
                print(f"Row Number: {self.rows_to_delete}")
                if self.data_handler is not None:
                    self.data_handler.fn_delete(self)

                df = self.grid.data.drop(self.rows_to_delete)  # Delete rows selected
                self.grid.data = df.reset_index(
                    drop=True
                )  # Must reset index so data grid can perform tasks to updated data frame after reload
                self.button_bar.message.value = markdown("  🗑️ _Deleted Row_ ")
                if self.grid._data["data"]:  # If data in grid
                    self.grid._round_sig_figs()
            else:
                self.button_bar.message.value = markdown(
                    "  👇 _Please select one row from the table!_"
                )
        except Exception as e:
            pass

    def _check_one_row_selected(self):
        if len(self.grid.selected_rows_) > 1:
            raise Exception(
                markdown("  👇 _Please only select ONLY one row from the table!_")
            )

    def _save(self):
        if self._edit_bool:  # If editing then use patch
            if self.data_handler is not None:
                self.data_handler.fn_patch(self)

            df = self.grid.data
            # ^ Can't assign directly to data so must assign to another variable before pushing changes through the setter.
            for (k, v,) in self.baseform.autowidget.value.items():
                df.loc[self.selected_row, k] = v
            # ^ update selected row with updated values

            self.grid.data = df  # Update data through setter
        else:  # Else, if adding values, use post
            if self.data_handler is not None:
                self.data_handler.fn_post(self)

            df = pd.DataFrame([self.baseform.autowidget.value])
            if not self.grid._data["data"]:  # If no data in grid
                self.grid.data = df
            else:
                # Append new row onto data frame and set to grid's data.
                self.grid.data = pd.concat([self.grid.data, df], ignore_index=True)
                # self.grid.data.append(
                #     self.baseform.autowidget.value, ignore_index=True
                # )

    def _onsave(self):
        self._display_grid()
        self._set_toggle_buttons_to_false()
        if self._edit_bool:  # If editing
            self.button_bar.message.value = markdown(
                "  💾 _Successfully updated row_ "
            )  # TODO: Make generic
        else:
            self.button_bar.message.value = markdown(
                "  💾 _Successfully added row_ "
            )  # TODO: Make generic

    def _backward(self):
        self._display_grid()

    def _revert(self):
        self.baseform.autowidget.value = self.initial_value

    def _set_toggle_buttons_to_false(self):
        if self.button_bar.add.value is True:
            self.button_bar.add.value = False
        elif self.button_bar.edit.value is True:
            self.button_bar.edit.value = False

    def _display_grid(self):
        if (
            self.button_bar.edit.value or self.button_bar.add.value
        ):  # Don't remove display of base form if already showing when going from edit to add (or vice versa).
            pass
        else:
            self._reload_all_data()  # Reloads all data and data grid
            self.baseform.layout.display = "none"  # Hides base form menu
            self._set_toggle_buttons_to_false()

    def _display_baseform(self):
        self.baseform.layout.display = "block"  # Displays base form menu

    def _reload_all_data(self):
        if self.data_handler is not None:
            self.value = self.data_handler.fn_get_all_data(self)
        if self.grid._data["data"]:  # If data in grid
            self.grid._round_sig_figs()

    def _set_value(self):
        self.data = pd.DataFrame(self.value)


if __name__ == "__main__":

    class DataFrameCols(BaseModel):
        string: str = Field("string", aui_column_width=100)
        integer: int = Field(1, aui_column_width=80)
        floater: float = Field(3.1415, aui_column_width=70, aui_sig_fig=3)
        something_else: float = Field(324, aui_column_width=100)

    class TestDataFrame(BaseModel):
        dataframe: typing.List[DataFrameCols] = Field(..., format="dataframe")

    schema = attach_schema_refs(TestDataFrame.schema())["properties"]["dataframe"][
        "items"
    ]
    editgrid = EditGrid(schema=schema)
    display(editgrid)

editgrid.grid.data.to_dict(orient="records")

editgrid.value


