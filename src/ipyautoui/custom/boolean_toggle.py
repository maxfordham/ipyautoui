"""
if someone wants a boolean type, but wants the widget to display words (e.g. "Yes" or "No") instead of True or False
not sure this has any value so haven't linked it to the autoui mapping yet! 
"""

import traitlets as tr
import ipywidgets as w


class BooleanToggleButtons(w.HBox):
    value = tr.Bool(allow_none=True)

    def __init__(self, options=["Yes", "No"], **kwargs):
        if len(options) != 2:
            raise ValueError(
                "for it to be a boolean widget the len of options must be 2"
            )

        super().__init__(**kwargs)
        self.widget = w.ToggleButtons(options=options)
        options = options + [None]
        self.map_bool = dict(zip(options, [True, False, None]))
        self._init_controls()
        self.children = [self.widget]
        self._update_value("")

    def _init_controls(self):
        self.widget.observe(self._update_value, "value")

    def _update_value(self, on_change):
        self.value = self.map_bool[self.widget.value]
