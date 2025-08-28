# +


import pathlib
import ipyvuetify as v
import traitlets as tr
import ipywidgets as w

from ipyautoui.constants import PATH_VJSF_TEMPLATE
from ipyautoui.autoui import AutoUiFileMethods, AutoRenderMethods
from ipyautoui.automapschema import _init_model_schema
from ipyautoui.autoui import (
    AutoObjectFormLayout,
    get_from_schema_root,
)
from ipyautoui.custom.title_description import TitleDescription
import logging
import json

logger = logging.getLogger(__name__)
# import ipyvue
# ipyvue.watch(PATH_VJSF_TEMPLATE.parent)  # for hot-reloading. currently not in use. requires watchdog


def rename_vjsf_schema_keys(obj, old="x_", new="x-"):  # NOTE: not in use
    """recursive function to replace all keys beginning x_ --> x-
    this allows schema Field keys to be definied in pydantic and then
    converted to vjsf compliant schema"""

    if type(obj) == list:
        for l in list(obj):
            if type(l) == str and l[0:2] == old:
                l = new + l[2:]
            if type(l) == list or type(l) == dict:
                l = rename_vjsf_schema_keys(l)
            else:
                pass
    if type(obj) == dict:
        for k, v in obj.copy().items():
            if k[0:2] == old:
                obj[new + k[2:]] = v
                del obj[k]
            if type(v) == list or type(v) == dict:
                v = rename_vjsf_schema_keys(v)
            else:
                pass
    else:
        pass
    return obj


class Vjsf(v.VuetifyTemplate):
    template_file = str(PATH_VJSF_TEMPLATE)
    vjsf_loaded = tr.Bool(False).tag(sync=True)
    value = tr.Dict(default_value={}).tag(sync=True)
    schema = tr.Dict().tag(sync=True)
    valid = tr.Bool(False).tag(sync=True)


# -
if __name__ == "__main__":
    from ipyautoui.demo_schemas import CoreIpywidgets
    from IPython.display import display

    schema = CoreIpywidgets.model_json_schema()
    ui = Vjsf(schema=schema)
    display(ui)

# +


class AutoVjsf(
    w.VBox, AutoObjectFormLayout, AutoUiFileMethods, AutoRenderMethods, TitleDescription
):
    _value = tr.Dict()
    """create a vuetify form using ipyvuetify using VJSF """

    def __init__(self, schema, **kwargs):
        super().__init__(**kwargs)

        self.model, schema = _init_model_schema(schema)
        if "value" in kwargs:
            value = self._get_value(kwargs["value"], self.path)
        else:
            value = None
        # list of actions to be called on save
        if value is None:
            self.autowidget = Vjsf(schema=schema)
        else:
            self.autowidget = Vjsf(schema=schema, value=value)
        self.vbx_widget = w.VBox(
            [self.autowidget]
        )  # seems messy but all container widgets expect vbx_widget...
        self._value = self.autowidget.value
        self._init_controls()
        self.children = [
            w.HBox([self.bn_showraw, self.savebuttonbar]),
            self.html_title,  # only showing title here as description in Vjsf
            self.vbx_widget,
            self.vbx_showraw,
        ]
        self.title = self.get_title()

    def get_title(self):  # TODO: put this in AutoObjectFormLayout
        return get_from_schema_root(self.schema, "title")

    @property
    def json(self):
        if self.model is not None:
            try:
                return self.model(**self.value).json(indent=4)
            except:
                logger.warning("pydantic validation failed")
                return json.dumps(self.value, indent=4)
        else:
            return json.dumps(self.value, indent=4)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # TODO: add validation
        self._value = value
        self.autowidget.value = self._value

    def _init_controls(self):
        self.autowidget.observe(self.update_value, "value")

    def update_value(self, on_change):
        self._value = self.autowidget.value

    @property
    def schema(self):
        return self.autowidget.schema


# -

if __name__ == "__main__":
    from ipyautoui.demo_schemas import CoreIpywidgets

    autowidget = AutoVjsf(
        schema=CoreIpywidgets,
    )
    display(autowidget)

if __name__ == "__main__":
    autowidget.show_savebuttonbar = False
    autowidget.show_description = False
    autowidget.show_title = False
    autowidget.show_raw = False

if __name__ == "__main__":
    autowidget.show_savebuttonbar = True
    autowidget.show_description = True
    autowidget.show_title = True
    autowidget.show_raw = True

if __name__ == "__main__":
    Renderer = AutoVjsf.create_autoui_renderer(schema)
    display(Renderer(path=pathlib.Path("test.json")))
