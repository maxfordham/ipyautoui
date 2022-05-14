# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
# %run __init__.py
# %load_ext lab_black

import ipyvuetify as v
import traitlets
import ipywidgets as widgets

from ipyautoui.constants import PATH_VJSF_TEMPLATE
from ipyautoui.autoui import AutoUiCommonMethods, SaveControls

# import ipyvue
# ipyvue.watch(PATH_VJSF_TEMPLATE.parent)  # for hot-reloading. currently not in use. requires watchdog


class Vjsf(v.VuetifyTemplate):
    template_file = str(PATH_VJSF_TEMPLATE)
    vjsf_loaded = traitlets.Bool(False).tag(sync=True)
    value = traitlets.Dict(default_value={}).tag(sync=True)
    schema = traitlets.Dict().tag(sync=True)
    valid = traitlets.Bool(False).tag(sync=True)


# -
if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic
    from IPython.display import display

    test = TestAutoLogic()
    sch = test.schema()
    ui = Vjsf(schema=sch)
    display(ui)


class AutoVjsf(widgets.VBox, AutoUiCommonMethods):
    _value = traitlets.Dict()
    """create a vuetify form using ipyvuetify using VJSF """

    def __init__(
        self,
        schema,
        value=None,
        path=None,
        fn_onsave=None,
        show_raw=True,
        save_controls: SaveControls = SaveControls.save_buttonbar,
    ):
        super().__init__()
        self.show_raw = show_raw
        self.show_description = False
        self.path = path
        self.model, schema = self._init_model_schema(schema)
        value = self._get_value(value, self.path)
        # list of actions to be called on save
        self.fn_onsave = fn_onsave
        if value is None:
            self.vui = Vjsf(schema=schema)
        else:
            self.vui = Vjsf(schema=schema, value=value)
        self._value = self.vui.value
        self.vbx_raw = widgets.HBox()
        self._init_AutoUiCommonMethods()
        self._init_vui_form()
        self._init_controls()
        self.save_controls = save_controls
        # self.save_buttonbar._unsaved_changes(
        #     False
        # )  # TODO: not sure why this is required

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # TODO: add validation
        self._value = value
        self.vui.value = self._value

    def _init_vui_form(self):
        self.ui_main = widgets.VBox()
        self.ui_main.children = [self.vui]
        li = list(self.children)
        li.append(self.ui_main)
        self.children = li

    def _init_controls(self):
        self.vui.observe(self.update_value, "value")

    def update_value(self, on_change):
        self._value = self.vui.value

    @property
    def sch(self):  # TODO: change to schema
        return self.vui.schema


if __name__ == "__main__":
    vui = AutoVjsf(schema=TestAutoLogic.schema(), path="test_vuetify.json")
    display(vui)

if __name__ == "__main__":
    Renderer = AutoVjsf.create_autoui_renderer(sch)
    display(Renderer(path="test.json"))
