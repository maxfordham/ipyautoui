# ---
# jupyter:
#   jupytext:
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
# %run __init__.py
# %load_ext lab_black

import pathlib
import functools
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, Markdown, clear_output
from datetime import datetime, date
from dataclasses import dataclass
from pydantic import BaseModel
from markdown import markdown
import immutables
import json
import traitlets as tr
import typing as ty
from enum import Enum

from ipyautoui.constants import MAP_JSONSCHEMA_TO_IPYWIDGET, BUTTON_WIDTH_MIN


# +
def save():
    print("save")


def revert():
    print("revert")


class SaveButtonBar(widgets.HBox):
    def __init__(
        self,
        save: ty.Callable = save,
        revert: ty.Callable = revert,
        fn_onsave: ty.Union[ty.Callable, ty.List[ty.Callable]] = lambda: None,
        unsaved_changes: bool = False,
    ):
        """
        UI save dialogue

        Args:
            save: ty.Callable, zero input fn called on click of save button
            revert: ty.Callable, zero input fn called on click of revert button
            fn_onsave: ty.Callable, additional action that can be added to save button click

        """
        self.fn_save = save
        self.fn_revert = revert
        self.fn_onsave = fn_onsave
        self.out = widgets.Output()
        self._init_form()
        self._init_controls()
        self.unsaved_changes.value = unsaved_changes

    def _init_form(self):
        super().__init__()
        self.unsaved_changes = widgets.ToggleButton(
            disabled=True, layout=widgets.Layout(width=BUTTON_WIDTH_MIN)
        )
        self.revert = widgets.Button(
            icon="fa-undo",
            tooltip="revert to last save",
            button_style="warning",
            style={"font_weight": "bold"},
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
        )  # ,button_style='success'
        self.save = widgets.Button(
            icon="fa-save",
            tooltip="save changes",
            button_style="success",
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.showraw = widgets.ToggleButton(
            icon="code",
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
            tooltip="show raw text data",
            style={"font_weight": "bold", "button_color": None},
        )
        self.message = widgets.HTML("")
        children = [self.unsaved_changes, self.revert, self.save]
        children.append(self.message)
        self.children = children

    def _init_controls(self):
        self.save.on_click(self._save)
        self.revert.on_click(self._revert)
        self.unsaved_changes.observe(self._observe_unsaved_changes, "value")

    def _save(self, click):
        self.fn_save()
        self.message.value = markdown(
            f'_changes saved: {datetime.now().strftime("%H:%M:%S")}_'
        )
        self._unsaved_changes(False)
        if isinstance(self.fn_onsave, ty.Callable):
            self.fn_onsave()
        elif isinstance(self.fn_onsave, list):
            [f() for f in self.fn_onsave]
        else:
            ValueError("fn_onsave must be zero-order func or list of zero-order funcs")

    def _revert(self, click):
        self.fn_revert()
        self.message.value = markdown(f"_UI reverted to last save_")
        self._unsaved_changes(False)

    def _observe_unsaved_changes(self, onchange):
        if self.unsaved_changes.value:
            self.unsaved_changes.button_style = "danger"
            self.unsaved_changes.icon = "circle"
            self.tooltip = "DANGER: changes have been made since the last save"
        else:
            self.unsaved_changes.button_style = "success"
            self.unsaved_changes.icon = "check"
            self.tooltip = "SAFE: no changes have been made since the last save"

    def _unsaved_changes(self, istrue: bool):  # TODO: deprecate this fn
        self.unsaved_changes.value = istrue


# -

if __name__ == "__main__":
    save_button_bar = SaveButtonBar()
    display(save_button_bar)


class ButtonBar(widgets.HBox):
    def __init__(
        self,
        add: ty.Callable,
        edit: ty.Callable,
        copy: ty.Callable,
        delete: ty.Callable,
        backward: ty.Callable,
        show_message: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)  # main container
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

    buttonbar = ButtonBar(
        add=add,
        edit=edit,
        copy=copy,
        delete=delete,
        backward=backward,
    )

    display(buttonbar)

