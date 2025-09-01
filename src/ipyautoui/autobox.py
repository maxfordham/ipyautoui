
"""create a simple row item for a form. contains some simple automated layout features
"""


# +
import logging
import ipywidgets as w
from IPython.display import display
import traitlets as tr
from ipyautoui.custom.title_description import TitleDescription

logger = logging.getLogger(__name__)


# +
# functions to format the box based on traits
SPACER = w.HBox(layout={"width": "48px"})

f1 = lambda self: [
    w.HBox(
        [
            SPACER,
            self.get_tgl,
            self.hbx_title_description,
        ]
    ),
    w.HBox([SPACER, self.widget]),
]
f2 = lambda self: [
    w.HBox(
        [
            self.get_tgl,
            self.hbx_title_description,
        ]
    ),
    self.widget,
]

f3 = lambda self: [
    w.HBox(
        [
            w.HBox([SPACER, self.widget]),
            self.hbx_title_description,
        ]
    )
]
f4 = lambda self: [
    w.HBox(
        [
            self.widget,
            self.hbx_title_description,
        ]
    )
]
f5 = lambda self: [
    w.VBox([self.hbx_title_description, w.HBox([SPACER, self.get_tgl]), self.widget])
]

f6 = lambda self: [
    w.VBox([self.hbx_title_description, w.HBox([self.get_tgl]), self.widget])
]

f7 = lambda self: [
    w.VBox(
        [
            self.hbx_title_description,
            w.HBox(
                [
                    SPACER,
                    self.widget,
                ]
            ),
        ]
    )
]

f8 = lambda self: [self.hbx_title_description, self.widget]

# (align_horizontal, nested, indent)
map_format = {
    (True, True, True): f1,
    (True, True, False): f2,
    (True, False, True): f3,
    (True, False, False): f4,
    (False, True, True): f5,
    (False, True, False): f6,
    (False, False, True): f7,
    (False, False, False): f8,
}


# -


class Nest:
    @property
    def get_tgl(self):
        if not hasattr(self, "tgl"):
            self.tgl = w.ToggleButton(
                description="show", layout={"width": "300px"}, tooltip="open/close"
            )
            self._init_controls_Nest()
        return self.tgl

    def _init_controls_Nest(self):
        self.tgl.observe(self._tgl, "value")

    def _tgl(self, on_change):
        if self.tgl.value:
            self.widget.layout.display = ""
        else:
            self.widget.layout.display = "None"


class AutoBox(w.VBox, Nest, TitleDescription):
    nested = tr.Bool(default_value=False)
    align_horizontal = tr.Bool(default_value=True).tag(sync=True)
    hide = tr.Bool(default_value=True).tag(sync=True)
    widget = tr.Any(
        default_value=w.ToggleButton(
            tooltip="placeholder...", layout={"width": "600px"}
        )
    )
    indent = tr.Bool(default_value=False)
    _value = tr.Any()

    @tr.observe("nested")
    def _nested(self, on_change):
        self.get_tgl
        self.format_box()
        if not self.nested:
            self.tgl.value = True
        self._tgl("")

    @tr.observe("align_horizontal")
    def _align_horizontal(self, on_change):
        self.format_box()

    @tr.observe("indent")
    def _indent(self, on_change):
        self.format_box()

    @tr.observe("widget")
    def _widget(self, on_change):
        self.format_box()

    @tr.observe("widget")
    def _widget_value(self, on_change):
        self._value = self.widget.value

    @tr.observe("hide")
    def _hide(self, on_change):
        if self.hide:
            self.layout.display = "None"
        else:
            self.layout.display = ""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.widget.value = value

    def __init__(self, **kwargs):
        super().__init__(**{k: v for k, v in kwargs.items() if k not in ["tooltip", "value"]})
        #  ^ tooltip issue: https://github.com/jupyter-widgets/ipywidgets/issues/3860
        self.format_box()

    @property
    def format_tuple(self):
        return (self.align_horizontal, self.nested, self.indent)

    def format_box(self):
        self.children = map_format[self.format_tuple](self)

    @classmethod
    def wrapped_widget(
        cls, widget_type, kwargs_box=None, kwargs_fromcaller=None, **kwargs
    ):
        if kwargs_fromcaller is None:
            kwargs_fromcaller = {}
        widget = widget_type(**{**kwargs_fromcaller, **kwargs})
        if kwargs_box is None:
            kwargs_box = {}
        kwargs_box["widget"] = widget
        return cls(**kwargs_box)


if __name__ == "__main__":
    bx = AutoBox(title="asdfasdf", description="description", nested=True)
    display(bx)

if __name__ == "__main__":
    (bx.align_horizontal, bx.nested, bx.indent) = True, True, True  # f1

if __name__ == "__main__":
    (bx.align_horizontal, bx.nested, bx.indent) = True, True, False  # f2

if __name__ == "__main__":
    (bx.align_horizontal, bx.nested, bx.indent) = (True, False, True)  # f3

if __name__ == "__main__":
    (bx.align_horizontal, bx.nested, bx.indent) = (True, False, False)  # f4

if __name__ == "__main__":
    (bx.align_horizontal, bx.nested, bx.indent) = False, True, True  # f5

if __name__ == "__main__":
    (bx.align_horizontal, bx.nested, bx.indent) = False, True, False  # f6

if __name__ == "__main__":
    (bx.align_horizontal, bx.nested, bx.indent) = False, False, True  # f7

if __name__ == "__main__":
    (bx.align_horizontal, bx.nested, bx.indent) = False, False, False  # f8

if __name__ == "__main__":
    di = {
        "title": "Uniclass System Description",
        "description": "System Description that matches a code within the Uniclass Ss tables. https://uniclass.thenbs.com/taxon/ss",
        "tooltip": "Created and used by the Autodesk Classification Manager for Revit",
    }
    bx1 = AutoBox(**di)
    display(bx1)

if __name__ == "__main__":
    di = {
        "title": "title",
        "description": "Description ...",
        "tooltip": "tooltip ...",
    }
    display(w.VBox(**di))
    #  ^ tooltip issue: https://github.com/jupyter-widgets/ipywidgets/issues/3860
