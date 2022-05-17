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
import traitlets
import typing
from enum import Enum

from ipyautoui.constants import DI_JSONSCHEMA_WIDGET_MAP, BUTTON_WIDTH_MIN


# +
def save():
    print("save")


def revert():
    print("revert")


class SaveButtonBar(widgets.HBox):
    def __init__(
        self,
        save: typing.Callable = save,
        revert: typing.Callable = revert,
        fn_onsave: typing.Union[
            typing.Callable, typing.List[typing.Callable]
        ] = lambda: None,
    ):
        """
        UI save dialogue 
        
        Args: 
            save: typing.Callable, zero input fn called on click of save button
            revert: typing.Callable, zero input fn called on click of revert button
            fn_onsave: typing.Callable, additional action that can be added to save button click
        
        """
        self.fn_save = save
        self.fn_revert = revert
        self.fn_onsave = fn_onsave
        self.out = widgets.Output()
        self._init_form()
        self._init_controls()

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
        self.message = widgets.HTML("a message")
        children = [self.unsaved_changes, self.revert, self.save]
        children.append(self.message)
        self.children = children

    def _init_controls(self):
        self.save.on_click(self._save)
        self.revert.on_click(self._revert)

    def _save(self, click):
        self.fn_save()
        self.message.value = markdown(
            f'_changes saved: {datetime.now().strftime("%H:%M:%S")}_'
        )
        self._unsaved_changes(False)
        if type(self.fn_onsave) == typing.Callable:
            self.fn_onsave()
        elif type(self.fn_onsave) == list:
            [f() for f in self.fn_onsave]
        else:
            ValueError("fn_onsave must be zero-order func or list of zero-order funcs")

    def _revert(self, click):
        self.fn_revert()
        self.message.value = markdown(f"_UI reverted to last save_")
        self._unsaved_changes(False)

    def _unsaved_changes(self, istrue: bool):
        self.unsaved_changes.value = istrue
        if istrue:
            self.unsaved_changes.button_style = "danger"
            self.unsaved_changes.icon = "circle"
            self.tooltip = "DANGER: changes have been made since the last save"
        else:
            self.unsaved_changes.button_style = "success"
            self.unsaved_changes.icon = "check"
            self.tooltip = "SAFE: no changes have been made since the last save"


# -

if __name__ == "__main__":
    save_button_bar = SaveButtonBar()
    display(save_button_bar)


