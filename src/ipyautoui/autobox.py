# ---
# jupyter:
#   jupytext:
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

"""create a simple row item for a form. contains some simple automated layout features
"""
# %run _dev_sys_path_append.py
# %load_ext lab_black

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
            self.html_title,
        ]
    ),
    self.widget,
]
f2 = lambda self: [
    w.HBox(
        [
            self.get_tgl,
            self.html_title,
        ]
    ),
    self.widget,
]

f3 = lambda self: [
    w.HBox(
        [
            w.HBox([SPACER, self.widget]),
            self.html_title,
        ]
    )
]
f4 = lambda self: [
    w.HBox(
        [
            self.widget,
            self.html_title,
        ]
    )
]
f5 = lambda self: [
    w.VBox([self.html_title, w.HBox([SPACER, self.get_tgl]), self.widget])
]

f6 = lambda self: [w.VBox([self.html_title,w.HBox([self.get_tgl ]), self.widget])]

f7 = lambda self: [
    w.VBox(
        [
            self.html_title,
            w.HBox(
                [
                    SPACER,
                    self.widget,
                ]
            ),
        ]
    )
]

f8 = lambda self: [self.html_title, self.widget]

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
            self.tgl = w.ToggleButton(description="show", layout={"width": "300px"})
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
    widget = tr.Any(default_value=w.ToggleButton(layout={"width": "600px"}))
    indent = tr.Bool(default_value=False)

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

    @tr.observe("hide")
    def _hide(self, on_change):
        if self.hide:
            self.layout.display = "None"
        else:
            self.layout.display = ""

    def __init__(self, **kwargs):
        self._update_title_description()
        # with self.hold_trait_notifications():
        super().__init__(**kwargs)
        self.format_box()

    @property
    def format_tuple(self):
        return (self.align_horizontal, self.nested, self.indent)

    def format_box(self):
        self.children = map_format[self.format_tuple](self)


if __name__ == "__main__":
    bx = AutoBox(title="asdfasdf", nested=True)
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


