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
# %run _dev_sys_path_append.py
# %run __init__.py
#
# %load_ext lab_black

import ipyvuetify as v
import traitlets as tr
import ipywidgets as w

from ipyautoui.constants import PATH_VJSF_TEMPLATE
from ipyautoui.autoui import AutoUiFileMethods, AutoRenderMethods
from ipyautoui.automapschema import _init_model_schema

# import ipyvue
# ipyvue.watch(PATH_VJSF_TEMPLATE.parent)  # for hot-reloading. currently not in use. requires watchdog


class Vjsf(v.VuetifyTemplate):
    template_file = str(PATH_VJSF_TEMPLATE)
    vjsf_loaded = tr.Bool(False).tag(sync=True)
    value = tr.Dict(default_value={}).tag(sync=True)
    schema = tr.Dict().tag(sync=True)
    valid = tr.Bool(False).tag(sync=True)


# -
if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic, TestAutoLogicSimple
    from IPython.display import display

    ui = Vjsf(schema=TestAutoLogicSimple)
    test = TestAutoLogic()
    schema = test.schema()
    ui = Vjsf(schema=schema)
    display(ui)

# +
from ipyautoui.autoipywidget import (
    AutoObjectFormLayout,
    make_bold,
    get_from_schema_root,
)


class AutoVjsf(AutoObjectFormLayout, AutoUiFileMethods, AutoRenderMethods):
    _value = tr.Dict()
    """create a vuetify form using ipyvuetify using VJSF """

    def __init__(
        self,
        schema,
        value=None,
        path=None,
        fns_onsave=None,
        show_raw=True,
        show_title=True,
    ):
        super().__init__()
        self.show_raw = show_raw
        self.show_description = False

        self.model, schema = _init_model_schema(schema)
        self.path = path
        value = self._get_value(value, self.path)
        # list of actions to be called on save
        self.fns_onsave = fns_onsave
        if value is None:
            self.vui = Vjsf(schema=schema)
        else:
            self.vui = Vjsf(schema=schema, value=value)
        self.show_title = show_title
        self.title.value = make_bold(self.get_title())
        self.description.value = self.get_description()
        self._value = self.vui.value
        self.vbx_raw = w.HBox()
        self._init_vui_form()
        self._init_controls()

    def get_description(self):  # TODO: put this in AutoObjectFormLayout
        return get_from_schema_root(self.schema, "description")

    def get_title(self):  # TODO: put this in AutoObjectFormLayout
        return get_from_schema_root(self.schema, "title")

    def display_showraw(self):
        self.autowidget.layout.display = "None"
        return self.json

    @property
    def json(self):
        if self.model is not None:
            return self.model(**self.value).json(indent=4)
        else:
            return json.dumps(self.value, indent=4)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # TODO: add validation
        self._value = value
        self.vui.value = self._value

    def _init_vui_form(self):
        self.autowidget = w.VBox()
        self.autowidget.children = [self.vui]
        li = list(self.children)
        li.append(self.autowidget)
        self.children = li

    def _init_controls(self):
        self.vui.observe(self.update_value, "value")

    def update_value(self, on_change):
        self._value = self.vui.value

    @property
    def schema(self):
        return self.vui.schema


# -

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogicSimple, TestAutoLogic

    vui = AutoVjsf(schema=TestAutoLogicSimple, path="test_vuetify.json")
    display(vui)

if __name__ == "__main__":
    vui.show_savebuttonbar = False
    vui.show_description = False
    vui.show_title = False
    vui.show_raw = False

if __name__ == "__main__":
    vui.show_savebuttonbar = True
    vui.show_description = True
    vui.show_title = True
    vui.show_raw = True

if __name__ == "__main__":
    Renderer = AutoVjsf.create_autoui_renderer(schema)
    display(Renderer(path="test.json"))
