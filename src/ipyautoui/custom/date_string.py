import ipywidgets as w
import traitlets as tr
from datetime import datetime


class DatePickerString(w.HBox):
    _value = tr.Unicode(allow_none=True, default_value=None)
    strftime_format = tr.Unicode(default_value="%Y-%m-%d")

    def __init__(self, **kwargs):
        """thin wrapper around ipywidgets.DatePicker that stores "value" as
        json serializable Unicode"""
        self.picker = w.DatePicker(**kwargs)
        self._init_controls()
        super().__init__(**kwargs)
        self.children = [self.picker]

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if type(value) == str:
            self.picker.value = datetime.strptime(value, self.strftime_format)
        else:
            self.picker.value = value

    def _init_controls(self):
        self.picker.observe(self._update_change, "value")
        self.observe(self._update_change, "strftime_format")
        # ts = [n for n in self.picker.trait_names() if n != "value" and n[0] != "_"]
        # for t in ts:
        #     self.picker.observe(self._update_change, t)
        # TODO: pass traits to picker

    def _get_value(self):
        try:
            return self.picker.value.strftime(self.strftime_format)
        except:
            return None

    def _update_change(self, on_change):
        self._value = self._get_value()
