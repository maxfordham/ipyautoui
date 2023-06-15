# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
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
# %run ../_dev_sys_path_append.py
# %run __init__.py
# %load_ext lab_black

import ipywidgets as w
import traitlets as tr
from ipyautoui.constants import DELETE_BUTTON_KWARGS, ADD_BUTTON_KWARGS


class SelectFrom(w.VBox):
    fn_onclick = tr.Callable(lambda v: print(f"do something: {str(v)}"))
    fn_get_options = tr.Callable(lambda: [])
    options = tr.List(default_value=[])
    title = tr.Unicode(default_value="")
    message = tr.Unicode(default_value="")
    select_multiple = tr.Bool(default_value=True)

    @tr.observe("options")
    def _observe_options(self, change):
        self.select.options = change["new"]

    @tr.observe("title")
    def _observe_title(self, change):
        self.html_title.value = change["new"]

    @tr.observe("message")
    def _observe_message(self, change):
        self.html_message.value = change["new"]

    def __init__(self, **kwargs):
        self._init_form()
        super().__init__(**kwargs)
        self._init_controls()
        self.children = [self.bbar, self.select]
        self.update_options()

    def _init_form(self):
        self.select = w.SelectMultiple()
        self.bn = w.Button()
        self.html_title = w.HTML()
        self.html_message = w.HTML()
        self.hbx_text = w.HBox([self.html_title, self.html_message])
        self.bbar = w.HBox([self.bn, self.hbx_text])

    def _init_controls(self):
        self.bn.on_click(self.onclick)
        self.select.observe(self._update_message, "value")

    def onclick(self, on_click):
        if self.map_options is None:
            [self.fn_onclick(v) for v in self.select.value]
        else:
            [self.fn_onclick(self.map_options[v]) for v in self.select.value]

    def update_options(self):
        options = self.fn_get_options()
        if isinstance(options, dict):
            self.map_options = options
            self.options = list(options.keys())
        elif isinstance(options, list):
            self.map_options = None
            self.options = options
        else:
            raise ValueError("options must be a list or dict")

    def _update_message(self, on_change):
        self.html_message.value = ", ".join(self.select.value)


class Remove(SelectFrom):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        {setattr(self.bn, k, v) for k, v in DELETE_BUTTON_KWARGS.items()}


class Add(SelectFrom):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        {setattr(self.bn, k, v) for k, v in ADD_BUTTON_KWARGS.items()}
