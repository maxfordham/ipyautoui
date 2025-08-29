import ipywidgets as w
import traitlets as tr
from IPython.display import display


class ComboboxMapped(w.Box):
    _value = tr.Unicode(allow_none=True)
    _options = tr.List(tr.Tuple(tr.Any(), tr.Any()), default_value=[])

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value in [o[0] for o in self.options]:
            self.widget.value = value
        elif value in [o[1] for o in self.options]:
            self.widget.value = self.options[[o[1] for o in self.options].index(value)][
                0
            ]
        else:
            if self.widget.ensure_option:
                raise ValueError(f"value {value} not in options")
            else:
                self.widget.value = value

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = self.validate_options(options)

    @tr.observe("_options")
    def _observe_options(self, change):
        self.widget.options = [o[0] for o in self.options]

    @staticmethod
    def validate_options(options):
        if isinstance(options, dict):
            return [(k, v) for k, v in options.items()]
        elif (
            isinstance(options, list)
            and len(options) > 1
            and isinstance(options[0], tuple)
        ):
            return options
        elif (
            isinstance(options, list)
            and len(options) > 1
            and not isinstance(options[0], tuple)
        ):
            return [(v, v) for v in options]
        else:
            # raise ValueError("options must be a dict, list of tuples, or list of values")
            return []

    def __init__(self, **kwargs):
        super().__init__()
        if not "options" in kwargs:
            # raise ValueError("options must be specified and must be a dict, list of tuples, or list of values")
            kwargs["options"] = []
        options = kwargs["options"]
        value = None
        if "value" in kwargs:
            value = kwargs["value"]
        if "ensure_option" not in kwargs:
            # default to True, but allow False
            kwargs["ensure_option"] = True

        kwargs.pop("options", None)
        kwargs.pop("value", None)
        self.widget = w.Combobox(**kwargs)
        self.children = [self.widget]
        self.options = self.validate_options(options)
        self._init_controls()
        if value is not None:
            self.value = value

    def _init_controls(self):
        self.widget.observe(self._update_value, "value")

    def _update_value(self, change):
        try:
            n = self.widget.options.index(self.widget.value)
            self._value = self.options[n][1]
        except Exception as e:
            if self.widget.ensure_option:
                raise ValueError(f"combobox value {self.widget.value} not in options")
            else:
                self._value = self.widget.value


if __name__ == "__main__":
    cmbx = ComboboxMapped(options={"A": "a", "B": "b"}, value="b")
    display(cmbx)

if __name__ == "__main__":
    print(cmbx.value)
