import ipywidgets as w
import traitlets as tr
from datetime import datetime


class DatePickerString(w.DatePicker):
    """extends DatePicker to save a jsonable string _value"""

    _value = tr.Unicode()
    strftime_format = tr.Unicode(default_value="%Y-%m-%d")

    @tr.observe("value")
    def _update_value_string(self, on_change):
        if self.value is not None:
            self._value = self.value.strftime(self.strftime_format)

    @tr.validate("value")
    def _validate_value(self, proposal):
        if isinstance(proposal["value"], str):
            return datetime.strptime(proposal["value"], self.strftime_format)
        else:
            return proposal["value"]


class NaiveDatetimePickerString(w.NaiveDatetimePicker):
    """extends DatetimePicker to save a jsonable string _value"""

    _value = tr.Unicode()
    strftime_format = tr.Unicode(default_value="%Y-%m-%dT%H:%M:%S")

    @tr.validate("value")  # set value. if string convert to datetime
    def _validate_value(self, proposal):
        if isinstance(proposal["value"], str):
            t = proposal["value"]
            if "." in t:
                t = t.split(".")[0]
            return datetime.strptime(t, self.strftime_format)
        else:
            return proposal["value"]

    @tr.observe("value")  # convert datetime to string
    def _update_value_string(self, on_change):
        if self.value is not None:
            self._value = self.value.strftime(self.strftime_format)
