# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.6
#   kernelspec:
#     display_name: Python [conda env:mf_base]
#     language: python
#     name: conda-env-mf_base-py
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

# from ipyautoui.displayfile import DisplayFiles
from ipyautoui import AutoUi, AutoUiConfig

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
        pydantic_model: typing.Type[BaseModel],
        save: typing.Callable,
        revert: typing.Callable,
        fn_onsave: typing.Callable = lambda: None,
    ):
        self.fn_save = save
        self.fn_revert = revert
        self.fn_onsave = fn_onsave
        self.pydantic_model = pydantic_model
        self.conf = AutoUiConfig(pydantic_model=pydantic_model, show_raw=False)
        self.out = widgets.Output()
        self._init_form()
        self._init_controls()

    def _init_form(self):
        super().__init__()  # main container
        self.auto_ui = AutoUi(
            pydantic_obj=self.pydantic_model(), config_autoui=self.conf,
        )
        self.save_button_bar = SaveButtonBar(
            save=self.fn_save, revert=self.fn_revert, fn_onsave=self.fn_onsave
        )
        # pydantic_model_name = spaces_before_capitals(
        #     type(self.pydantic_model()).__name__
        # )
        # self.title = widgets.HTML(markdown(f"# _{pydantic_model_name} Menu_"))
        self.title = widgets.HTML()
        self.children = [self.title, self.save_button_bar, self.auto_ui]

    def _init_controls(self):
        for k, v in self.auto_ui.di_widgets.items():
            if v.has_trait("value"):
                v.observe(
                    functools.partial(self._watch_change, key=k, watch="value"), "value"
                )
            elif v.has_trait("_value"):
                v.observe(
                    functools.partial(self._watch_change, key=k, watch="_value"),
                    "_value",
                )

    @property
    def to_dict(self):
        """JSON serialisation occurs and produces dictionary."""
        # return self.auto_ui.pydantic_obj.dict(by_alias=True)
        return json.loads(self.auto_ui.pydantic_obj.json(by_alias=True))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        """The setter allows a user to pass a new value field to the class."""
        if value is not None:
            self._value = value
        self._set_value()

    def _watch_change(self, change, key=None, watch="value"):
        if hasattr(self, "save_button_bar"):
            self.save_button_bar._unsaved_changes(True)

    def _set_value(self):
        self.auto_ui.pydantic_obj = self.pydantic_model(**self.value)
        self.save_button_bar._unsaved_changes(False)


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
        self.copy = widgets.ToggleButton(
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
        self.copy.observe(self._copy, "value")
        self.delete.on_click(self._delete)

    def _add(self, onchange):
        self._reset_message()
        if self.add.value:
            if self.edit.value:
                self.edit.value = False  # If Edit button already clicked on and add is then clicked on then, trigger toggle for Edit button.
            elif self.copy.value:
                self.copy.value = False  # Similar as above but for copy button
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
            elif self.copy.value:
                self.copy.value = False
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
        if self.copy.value:
            if self.add.value:
                self.add.value = False
            if self.edit.value:
                self.edit.value = False
            self.copy.tooltip = "Go back to table"
            self.copy.layout.border = TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT
            self.fn_copy()
            if self.show_message:
                self.message.value = markdown("  📝 _Copying Value_ ")
        else:
            self._reset_message()
            self.copy.tooltip = "copy"
            self.copy.layout.border = None
            self.copy.icon = "copy"
            self.copy.button_style = "primary"
            self.fn_backward()

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
        print("EDIT")

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
        pydantic_model: typing.Type[BaseModel],
        df: pd.DataFrame = None,
        kwargs_datagrid_default: frozenmap = frozenmap(),
        kwargs_datagrid_update: frozenmap = frozenmap(),
        ignore_cols: list = [],
    ):
        # Put all objects in datagrid beloning to that particular model
        self.pydantic_model = pydantic_model
        if df is None:
            df = pd.DataFrame([self.pydantic_model().dict(by_alias=True)])
            # df = pd.DataFrame([json.loads(self.pydantic_model().json(by_alias=True))])

        self._check_data(
            df, ignore_cols
        )  # Checking data frame satisfies pydantic model

        self.kwargs_datagrid_default = kwargs_datagrid_default
        self._init_form(df)
        self.kwargs_datagrid_update = kwargs_datagrid_update

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
            k: v["aui_sig_fig"]
            for k, v in self.pydantic_model().schema()["properties"].items()
            if "aui_sig_fig" in v
        }
        return self._aui_sig_figs

    @property
    def aui_column_widths(self):
        self._aui_column_widths = {
            k: v["aui_column_width"]
            for k, v in self.pydantic_model().schema()["properties"].items()
            if "aui_column_width" in v
        }  # Obtaining column widths from pydantic schema object
        return self._aui_column_widths

    @property
    def datetime_format_renderers(self):
        date_time_fields = {
            k: v["format"]
            for k, v in self.pydantic_model().schema()["properties"].items()
            if "format" in v
        }
        text_renderer_date_time_format = TextRenderer(
            format="%Y-%m-%d %H:%M:%S", format_type="time",
        )
        return {k: text_renderer_date_time_format for k, v in date_time_fields.items()}

    @property
    def column_names(self):
        return [k for k, v in self.pydantic_model().schema()["properties"].items()]

    def _round_sig_figs(self):
        df = self.data
        for k, v in self.aui_sig_figs.items():
            df.loc[:, k] = df.loc[:, k].apply(lambda x: round_sig_figs(x, sig_figs=v))
        self.data = df  # Update data through setter

    def _set_column_widths(self):
        self.column_widths = self.aui_column_widths  # Set column widths for data grid.

    def _check_data(self, df, ignore_cols):
        """Checking column names in produced data frame match those within the pydantic model."""
        columns = [column for column in df.columns if column not in ignore_cols]
        if not collections.Counter(columns) == collections.Counter(self.column_names):
            raise Exception(
                f"Pydantic model fields and data fields do not match.\nRejected Columns: {list(set(columns).difference(self.column_names))}"
            )

    @classmethod
    def from_dict(cls, pydantic_model, li, ignore_cols=[]):
        df = pd.DataFrame(li)
        return cls(pydantic_model=pydantic_model, df=df, ignore_cols=ignore_cols)


class DataHandler(BaseModel):
    fn_get_all_data: typing.Callable
    fn_post: typing.Callable
    fn_patch: typing.Callable
    fn_delete: typing.Callable


class EditGrid(widgets.VBox, traitlets.HasTraits):

    _value = traitlets.List()

    def __init__(
        self,
        pydantic_model: typing.Type[BaseModel],
        df: pd.DataFrame = None,
        data_handler: typing.Type[BaseModel] = None,
        kwargs_datagrid_default: frozenmap = {},
        kwargs_datagrid_update: frozenmap = {},
        ignore_cols: list = [],
    ):
        self.data_handler = data_handler
        if self.data_handler is not None:
            df = pd.DataFrame(self.data_handler.fn_get_all_data(self))
        self.pydantic_model = pydantic_model
        self.out = widgets.Output()
        self._init_form(
            df=df,
            kwargs_datagrid_default=kwargs_datagrid_default,
            kwargs_datagrid_update=kwargs_datagrid_update,
            ignore_cols=ignore_cols,
        )
        self._init_controls()
        self._edit_bool = False  # Initially define edit mode to be false

    def _init_form(
        self, df, kwargs_datagrid_default, kwargs_datagrid_update, ignore_cols,
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
            pydantic_model=self.pydantic_model,
            df=df,
            kwargs_datagrid_default=kwargs_datagrid_default,
            kwargs_datagrid_update=kwargs_datagrid_update,
            ignore_cols=ignore_cols,
        )
        self.base_form = BaseForm(
            pydantic_model=self.pydantic_model,
            save=self._save,
            revert=self._revert,
            fn_onsave=self._onsave,
        )
        self.base_form.title.value = ""
        self.button_bar.layout = widgets.Layout(padding="0px 20px")
        self.base_form.save_button_bar.layout = widgets.Layout(padding="0px 20px")
        self.base_form.layout = widgets.Layout(padding="0px 0px 40px 0px")
        self.children = [self.button_bar, self.base_form, self.grid]
        self.base_form.layout.display = "none"  # Hide base form menu

    def _init_controls(self):
        self.grid.observe(self._update_baseform, "selections")

    def _update_baseform(self, onchange):
        if self.base_form.layout.display == "block":
            self.base_form.value = self.di_row
        if (
            self.button_bar.add.value
        ):  # When on add and then select row, we are essentially copying so set copy button to True.
            self.button_bar.add.value = False
            self.button_bar.copy.value = True

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
            self.initial_value = self.pydantic_model()  # Obtain default value.
            self.base_form.value = dict(self.initial_value)
            self._display_base_form()
            self.button_bar.message.value = markdown("  ➕ _Adding Value_ ")
        except Exception as e:
            print(e)
            self.button_bar.message.value = markdown("  ☠️ _Failed to add_")

    def _edit(self):
        try:
            di_obj = self.di_row
            self.initial_value = self.pydantic_model(**di_obj)
            self.base_form.value = di_obj  # Set values in fields
            self._display_base_form()
            self.button_bar.message.value = markdown("  ✏️ _Editing Value_ ")
            self._edit_bool = True  # Editing mode is True
        except Exception as e:
            self.button_bar.edit.value = False
            self.button_bar.message.value = markdown(
                "  👇 _Please select one row from the table!_ "
            )

    def _copy(self):
        try:
            di_obj = self.di_row
            self.initial_value = self.pydantic_model(**di_obj)
            self.base_form.value = di_obj  # Set values in fields
            self._display_base_form()
            self.button_bar.message.value = markdown("  📝 _Copying Value_ ")
            self._edit_bool = False  # Want to add the values
        except Exception as e:
            self.button_bar.copy.value = False
            self.button_bar.message.value = markdown(
                "  👇 _Please select one row from the table!_ "
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
        if len(self.grid.selected_rows) > 1:
            raise Exception(
                markdown("  👇 _Please only select one row from the table!_")
            )
        for r_select in self.grid.selected_rows:
            if r_select["r1"] < r_select["r2"]:
                raise Exception(
                    markdown("  👇 _Please only select one row from the table!_")
                )

    def _save(self):
        if self._edit_bool:  # If editing then use patch
            if self.data_handler is not None:
                self.data_handler.fn_patch(self)

            df = (
                self.grid.data
            )  # Can't assign directly to data so must assign to another variable before pushing changes through the setter.
            for (
                k,
                v,
            ) in (
                self.base_form.to_dict.items()
            ):  # update selected row with updated values
                df.loc[self.selected_row, k] = v

            self.grid.data = df  # Update data through setter
        else:  # Else, if adding values, use post
            if self.data_handler is not None:
                self.data_handler.fn_post(self)

            if not self.grid._data["data"]:  # If no data in grid
                self.grid.data = pd.DataFrame([self.base_form.to_dict])
            else:
                # Append new row onto data frame and set to grid's data.
                self.grid.data = self.grid.data.append(
                    self.base_form.to_dict, ignore_index=True
                )

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
        obj_revert = deepcopy(self.initial_value)
        self.base_form.auto_ui.pydantic_obj = obj_revert

    def _set_toggle_buttons_to_false(self):
        if self.button_bar.copy.value is True:
            self.button_bar.copy.value = False
        elif self.button_bar.add.value is True:
            self.button_bar.add.value = False
        elif self.button_bar.edit.value is True:
            self.button_bar.edit.value = False

    def _display_grid(self):
        if (
            self.button_bar.edit.value
            or self.button_bar.add.value
            or self.button_bar.copy.value
        ):  # Don't remove display of base form if already showing when going from edit to add (or vice versa).
            pass
        else:
            self._reload_all_data()  # Reloads all data and data grid
            self.base_form.layout.display = "none"  # Hides base form menu
            self._set_toggle_buttons_to_false()

    def _display_base_form(self):
        self.base_form.layout.display = "block"  # Displays base form menu

    def _reload_all_data(self):
        if self.data_handler is not None:
            self.value = self.data_handler.fn_get_all_data(self)
        if self.grid._data["data"]:  # If data in grid
            self.grid._round_sig_figs()

    def _set_value(self):
        self.data = pd.DataFrame(self.value)


