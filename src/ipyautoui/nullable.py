import functools
import ipywidgets as w
import traitlets as tr

from ipyautoui.constants import BUTTON_WIDTH_MIN
from ipyautoui._utils import is_null

SHOW_NONE_KWARGS = dict(value="None", disabled=True, layout={"display": "None"})


def _get_value_trait(obj_with_traits):
    """gets the trait type for a given object
    (looks for "_value" and "value" allowing use of setters and getters)
    Args:
        obj_with_traits (traitlets.Type): obj with traits
    Raises:
        ValueError: if "value" trait not exist
    Returns:
        typing.Type: trait type of traitlet
    """
    try:
        return obj_with_traits.traits()["value"]
    except:
        try:
            return obj_with_traits.traits()["_value"]
        except:
            raise ValueError(
                f"{str(type(obj_with_traits))}: has no 'value' or '_value' trait"
            )


class Nullable(w.HBox):
    """class to allow widgets to be nullable. The widget that is extended is accessed
    using `self.widget`"""

    disabled = tr.Bool(default_value=False)
    nullable = tr.Bool(default_value=True)

    @tr.observe("disabled")
    def observe_disabled(self, on_change):
        """If disabled, ensure that the widget is disabled and the button is also."""
        if self.disabled:
            if self.widget.value is not None:
                self.bn.value = False
            else:
                self.bn.value = True
            self.bn.disabled = True
            self.widget.disabled = True
        else:
            self.bn.disabled = False
            self.widget.disabled = False

    def __init__(self, widget_type, *args, **kwargs):
        # self.schema = schema
        # self.caller = create_widget_caller(schema)
        # ^ TODO: should this be in a higher-level func?
        #         ui = nullable(w.IntSlider)(value=30) # this doesn't work bu maybe should...
        self.nullable = True
        self.bn = w.ToggleButton(icon="toggle-on", layout={"width": BUTTON_WIDTH_MIN})
        self.show_none = w.Text(**SHOW_NONE_KWARGS)
        if "value" in kwargs.keys():
            value = kwargs["value"]
        elif len(args) > 0:
            value = args[0]
        else:
            value = None
        self.widget = widget_type(*args, **kwargs)
        self._init_trait()
        super().__init__([self.bn, self.widget, self.show_none])
        self._init_controls()
        self.value = value

    def _init_trait(self):
        # NOTE: see test for add_traits that demos usage  -@jovyan at 7/18/2022, 12:11:39 PM
        # https://github.com/ipython/ipython/commit/5105f02df27456cc54867dfbe4cef60d91021f92
        trait_type = type(_get_value_trait(self.widget))
        self.add_traits(**{"_value": trait_type(allow_none=True)})

    @property
    def value(self):
        return self._value

    def update_value(self, value):
        self.bn.value = False
        self.widget.value = value
        # note. as the self.widget.value still exists in the background,
        #       this may not trigger a change event...
        #       so we'll manually do it too (below)
        self.fn_update("")

    @value.setter
    def value(self, value):
        if is_null(value):
            self.bn.value = True
            self._value = None
        else:
            self.update_value(value)

    def _init_controls(self):
        self.bn.observe(self._toggle_none, "value")
        for watch in ["_value", "value"]:
            if watch in self.widget.trait_names():
                self.fn_update = functools.partial(self._update, name=watch)
                self.widget.observe(self.fn_update)
                break
        self.observe(self._observe_nullable, "nullable")

    def _observe_nullable(self, onchange):
        if self.nullable:
            self.bn.layout.display = ""
        else:
            self.bn.layout.display = "None"

    def _update(self, onchange, name="_value"):
        self._value = getattr(self.widget, name)

    def _toggle_none(self, onchange):
        if self.bn.value:
            self.bn.icon = "toggle-off"
            self.widget.layout.display = "None"
            self.show_none.layout.display = ""
            self.value = None
        else:
            self.bn.icon = "toggle-on"
            self.widget.layout.display = ""
            self.show_none.layout.display = "None"
            if self.widget.value is not None:
                self.value = self.widget.value


def nullable(fn, **kwargs):
    """extend a simple widget to allow None

    Args:
        fn (widget_type): e.g. w.IntText

    Returns:
        Nullable: a HBox that contains a the widget `widget`.
    """
    nm = fn.__name__
    partial_func = functools.partial(Nullable, fn, **kwargs)
    functools.update_wrapper(partial_func, Nullable)
    partial_func.__name__ = Nullable.__name__ + nm
    return partial_func
