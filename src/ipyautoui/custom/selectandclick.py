# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %run ../_dev_sys_path_append.py
# %run __init__.py
# %load_ext lab_black

# +
import ipywidgets as w
import traitlets as tr
from ipyautoui.constants import DELETE_BUTTON_KWARGS, ADD_BUTTON_KWARGS


class SelectAndClick(w.Box):
    fn_onclick = tr.Callable(lambda v: print(f"do something: {str(v)}"))
    fn_get_options = tr.Callable(lambda: [])
    options = tr.List(default_value=[])  # allow dict ?
    title = tr.Unicode(default_value="")
    message = tr.Unicode(default_value="")
    align_horizontal = tr.Bool(default_value=True)
    align_left = tr.Bool(default_value=True)

    @tr.observe("align_horizontal")
    def _observe_align_horizontal(self, change):
        self.align()

    @tr.observe("align_left")
    def _observe_align_left(self, change):
        self.align()

    def align(self):
        # up-down
        if self.align_horizontal:
            self.layout.display = "flex"
            self.layout.flex_flow = "row"
            self.layout.align_items = "stretch"
        else:
            self.layout.display = "flex"
            self.layout.flex_flow = "column"
            self.layout.align_items = "stretch"
        # left-right
        if self.align_left and self.align_horizontal:
            self.children = [self.select, self.hbx_bbar]
            self.hbx_text.children = [self.html_title, self.html_message]
            self.hbx_bbar.children = [self.bn, self.hbx_text]
        elif self.align_left and not self.align_horizontal:
            self.children = [self.hbx_bbar, self.select]
            self.hbx_text.children = [self.html_title, self.html_message]
            self.hbx_bbar.children = [self.bn, self.hbx_text]
        elif not self.align_left and not self.align_horizontal:
            self.children = [self.hbx_bbar, self.select]
            self.hbx_text.children = [self.html_title, self.html_message]
            self.hbx_bbar.children = [self.bn, self.hbx_text]
        else:
            self.children = [self.hbx_bbar, self.select]
            self.hbx_text.children = [self.html_message, self.html_title]
            self.hbx_bbar.children = [self.hbx_text, self.bn]

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

        self.update_options()
        self._observe_align_horizontal("")
        self._observe_align_left("")

    def _init_form(self):
        self.select = self.get_selector_widget()
        self.bn = w.Button()
        self.html_title = w.HTML()
        self.html_message = w.HTML()
        self.hbx_text = w.HBox()
        self.hbx_bbar = w.HBox()

    def _init_controls(self):
        self.bn.on_click(self.onclick)
        self.select.observe(self._update_message, "value")

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

    def onclick(self, on_click):
        if self.map_options is None:
            self.fn_onclick(self.select.value)
        else:
            self.fn_onclick(self.map_options[self.select.value])

    @tr.default("align_horizontal")
    def default_align_horizontal(self):
        return True

    @tr.default("align_left")
    def default_align_leftl(self):
        return True

    @staticmethod
    def get_selector_widget():
        return w.Combobox(ensure_option=True)



# -

class SelectMultipleAndClick(SelectAndClick):
    def onclick(self, on_click):
        if self.map_options is None:
            [self.fn_onclick(v) for v in self.select.value]
        else:
            [self.fn_onclick(self.map_options[v]) for v in self.select.value]

    @tr.default("align_horizontal")
    def default_align_horizontal(self):
        return False

    @tr.default("align_left")
    def default_align_left(self):
        return True

    @staticmethod
    def get_selector_widget():
        return w.SelectMultiple()


if __name__ == "__main__":
    ui = SelectAndClick(
        fn_get_options=lambda: ["a", "b", "c"],
        title="asdf",
        align_horizontal=False,
    )
    display(ui)


# +
class RemoveMultiple(SelectMultipleAndClick):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        {setattr(self.bn, k, v) for k, v in DELETE_BUTTON_KWARGS.items()}


class AddMultiple(SelectMultipleAndClick):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        {setattr(self.bn, k, v) for k, v in ADD_BUTTON_KWARGS.items()}


# -

if __name__ == "__main__":
    ui = AddMultiple(
        fn_get_options=lambda: ["a", "b", "c"],
        align_horizontal=False,
        title="<b>asdf |</b>",
    )
    display(ui)

if __name__ == "__main__":
    ui.align_horizontal = True

if __name__ == "__main__":
    ui.align_horizontal = False
    ui.align_left = False


