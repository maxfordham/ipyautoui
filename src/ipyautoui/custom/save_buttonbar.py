# ---
# jupyter:
#   jupytext:
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
import logging

from ipyautoui.constants import (
    MAP_JSONSCHEMA_TO_IPYWIDGET,
    BUTTON_WIDTH_MIN,
    TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT,
)


# +
def merge_callables(callables: ty.Union[ty.Callable, ty.List[ty.Callable]]):
    if isinstance(callables, ty.Callable):
        return callables
    elif isinstance(callables, ty.List):
        return lambda: [c() for c in callables if isinstance(c, ty.Callable)]
    else:
        raise ValueError("callables must be a callable or list of callables")


class SaveActions(tr.HasTraits):
    unsaved_changes = tr.Bool(default_value=False)
    fns_onsave = tr.List(trait=tr.Callable())
    fns_onrevert = tr.List(trait=tr.Callable())

    @tr.default("fns_onsave")
    def _default_fns_onsave(self):
        s = f"fns_onsave - action called @ {datetime.now().strftime('%H:%M:%S')}"
        log_fns_onsave = lambda: logging.info(s)
        log_fns_onsave.__name__ = "log_fns_onsave"
        print_fns_onsave = lambda: print(s)
        print_fns_onsave.__name__ = "print_fns_onsave"
        return [log_fns_onsave, print_fns_onsave]

    @tr.default("fns_onrevert")
    def _default_fn_revert(self):
        s = f"log_fns_onrevert - action called @ {datetime.now().strftime('%H:%M:%S')}"
        log_fns_onrevert = lambda: logging.info(s)
        log_fns_onrevert.__name__ = "log_fns_onrevert"
        print_fns_onrevert = lambda: print(s)
        print_fns_onrevert.__name__ = "print_fns_onrevert"
        return [log_fns_onrevert, print_fns_onrevert]

    def fn_save(self):
        """do not edit"""
        return merge_callables(self.fns_onsave)()

    def fn_revert(self):
        return merge_callables(self.fns_onrevert)()

    def _add_action(self, action_name, fn_add, avoid_dupes=True, overwrite_dupes=True):
        fns = getattr(self, action_name)
        if avoid_dupes:
            names = [f.__name__ for f in getattr(self, action_name)]
            if fn_add.__name__ in names:
                if not overwrite_dupes:
                    raise ValueError(
                        f"ERROR: appending to {action_name}: {fn_add.__name__ } already exists in function names: {str(names)}"
                    )
                else:
                    fns = [f for f in fns if f.__name__ != fn_add.__name__]

        setattr(self, action_name, fns + [fn_add])

    def fns_onsave_add_action(
        self, fn: ty.Callable, avoid_dupes: bool = True, overwrite_dupes: bool = True
    ):
        self._add_action(
            "fns_onsave", fn, avoid_dupes=avoid_dupes, overwrite_dupes=overwrite_dupes
        )

    def fns_onrevert_add_action(
        self, fn: ty.Callable, avoid_dupes: bool = True, overwrite_dupes: bool = True
    ):
        self._add_action(
            "fns_onrevert", fn, avoid_dupes=avoid_dupes, overwrite_dupes=overwrite_dupes
        )


if __name__ == "__main__":
    actions = SaveActions()
    f = lambda: print("test")
    f.__name__ = "asdf"
    f1 = lambda: print("test1")
    f1.__name__ = "asdf"

    actions.fns_onsave_add_action(f)
    actions.fns_onsave_add_action(f1)
    actions.fn_save()

    actions.fns_onrevert_add_action(f)
    actions.fns_onrevert_add_action(f1)
    actions.fn_revert()


# +
class SaveButtonBar(widgets.HBox):
    save_actions = tr.Instance(klass=SaveActions, default_value=SaveActions())

    def __init__(self, **kwargs):
        super().__init__()
        self._init_form()
        self._init_controls()
        [setattr(self, k, v) for k, v in kwargs.items()]

    def _init_form(self):
        self.tgl_unsaved_changes = widgets.ToggleButton(
            disabled=True, layout=widgets.Layout(width=BUTTON_WIDTH_MIN)
        )
        self.bn_save = widgets.Button(
            icon="fa-save",
            tooltip="save changes",
            button_style="success",
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.bn_revert = widgets.Button(
            icon="fa-undo",
            tooltip="revert to last save",
            button_style="warning",
            style={"font_weight": "bold"},
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.message = widgets.HTML("")
        self.children = [
            self.tgl_unsaved_changes,
            self.bn_revert,
            self.bn_save,
            self.message,
        ]
        self.unsaved_changes = True
        self._observe_tgl_unsaved_changes("change")

    def _init_controls(self):
        self.bn_save.on_click(self._save)
        self.bn_revert.on_click(self._revert)
        self.save_actions.observe(
            self._observe_save_actions_unsaved_changes, "unsaved_changes"
        )
        self.tgl_unsaved_changes.observe(self._observe_tgl_unsaved_changes, "value")

    def _save(self, click):
        self.save_actions.fn_save()
        self.message.value = markdown(
            f'_changes saved: {datetime.now().strftime("%H:%M:%S")}_'
        )
        self.save_actions.unsaved_changes = False

    def _revert(self, click):
        self.save_actions.fn_revert()
        self.message.value = markdown(f"_UI reverted to last save_")
        self.save_actions.unsaved_changes = False

    def _observe_save_actions_unsaved_changes(self, onchange):
        self.tgl_unsaved_changes.value = self.save_actions.unsaved_changes

    def _observe_tgl_unsaved_changes(self, onchange):
        if self.tgl_unsaved_changes.value:
            self.tgl_unsaved_changes.button_style = "danger"
            self.tgl_unsaved_changes.icon = "circle"
            self.tgl_unsaved_changes.tooltip = (
                "DANGER: changes have been made since the last save"
            )
        else:
            self.tgl_unsaved_changes.button_style = "success"
            self.tgl_unsaved_changes.icon = "check"
            self.tgl_unsaved_changes.tooltip = (
                "SAFE: no changes have been made since the last save"
            )


if __name__ == "__main__":
    sb = SaveButtonBar()
    display(sb)
# -

if __name__ == "__main__":
    sb.save_actions.unsaved_changes = True


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
