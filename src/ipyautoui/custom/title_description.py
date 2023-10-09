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
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

"""generic support for observed title and description"""
# %run ../_dev_sys_path_append.py
# %load_ext lab_black

import traitlets as tr
import ipywidgets as w


class TitleDescription(tr.HasTraits):
    title = tr.Unicode(default_value=None, allow_none=True)
    description = tr.Unicode(default_value=None, allow_none=True)
    show_title = tr.Bool(default_value=True)

    @tr.observe("title")
    def observe_title(self, on_change):
        self._update_title_description()

    @tr.observe("description")
    def observe_description(self, on_change):
        self._update_title_description()

    @tr.observe("show_title")
    def observe_show_title(self, on_change):
        self._update_title_description()

    def _update_title_description(self):
        if not hasattr(self, "html_title"):
            self.html_title = w.HTML()
        if not self.show_title:
            self.html_title.layout.display = "None"
        else:
            if self.title is None and self.description is None:
                self.html_title.layout.display = "None"
            else:
                self.html_title.layout.display = ""
                get = lambda v: "" if v is None else v
                get_des = lambda v: "" if v is None else ", " + v
                self.html_title.value = (
                    f"<b>{get(self.title)}</b><i>{get_des(self.description)}</i>"
                )

    def __init__(self, **kwargs):
        super(TitleDescription, self).__init__(**kwargs)


if __name__ == "__main__":

    class Test(w.HBox, TitleDescription):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.children = [w.Button(icon="help"), self.html_title]

    t = Test(title="title", description="description")
    display(t)
