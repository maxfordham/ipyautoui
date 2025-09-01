# +
"""
# REF: copy and pasted in full from:
# https://github.com/stas-prokopiev/ipywidgets_toggle_buttons
"""



# +
# Standard library imports
import logging
from collections import OrderedDict
from abc import abstractmethod

# Third party imports
import ipywidgets as w
import traitlets as tr

# Local imports
DICT_LAYOUT_VBOX_ANY = dict(
    flex_flow="column wrap",
    width="100%",
    justify_content="center",
    align_self="center",
    padding="0px 0px 10px 0px",
)

DICT_LAYOUT_HBOX_ANY = dict(
    flex_flow="row wrap",
    # flex="1 1 auto",
    width="100%",
    justify_content="center",
    align_self="center",
    padding="10px 0px 0px 0px",
)

LOGGER = logging.getLogger(__name__)


class BaseToggleButtons(w.Box):
    """Abstract class for all toggle buttons

    Values are stored in self.widget_parent when displayed is self.widget
    Which is updated in the moment when display() is launched
    """

    align_horizontal = tr.Bool(default_value=True)

    @tr.observe("align_horizontal")
    def _align_horizontal(self, on_change):
        if self.align_horizontal:
            self.layout = DICT_LAYOUT_HBOX_ANY
        else:
            self.layout = DICT_LAYOUT_VBOX_ANY

    def __init__(self, widget_parent, **kwargs):
        """Initialize object"""
        self.widget_parent = widget_parent
        self.observe = self.widget_parent.observe
        super().__init__(layout=DICT_LAYOUT_VBOX_ANY)
        self._align_horizontal("")
        self._tuple_value_types = (str, list, tuple)
        #####
        # self._get_button_width = self._get_buttons_min_width_needed

    @abstractmethod
    def _update_widget_view(self):
        """ABSTRACT: Update view of widget according to self.widget_parent"""

    @abstractmethod
    def _update_buttons_for_new_options(self):
        """ABSTRACT: Update buttons if options were changed"""

    @property
    def value(self):
        """Getter for value used in widget"""
        return self.widget_parent.value

    @value.setter
    def value(self, new_value):
        """Setter for value used in widget with update of widget view

        Args:
            new_value (Any): Value to set for widget
        """
        if new_value != self.value:
            self.widget_parent.value = self._check_type_of_new_value(new_value)
            self._update_widget_view()

    @property
    def options(self):
        """Getter for options used in widget"""
        return self.widget_parent.options

    @options.setter
    def options(self, new_value):
        """Setter for options used in widget with update of widget view

        Args:
            new_value (list or tuple): New options to set for widgets
        """
        if new_value is None:
            new_value = []
        if set(new_value) == set(self.options):
            return None
        self.widget_parent.options = new_value
        self._update_buttons_for_new_options()

    def _check_type_of_new_value(self, new_value):
        """Check that the new value has right type"""
        if not isinstance(new_value, self._tuple_value_types):
            raise ValueError(
                f"New value for widget should be: {self._tuple_value_types}"
                f"but not: {type(new_value)}"
            )
        if hasattr(self, "max_chosen_values"):
            LOGGER.debug("Max number of pressed buttons reached")
            new_value = new_value[-self.max_chosen_values :]
        return new_value

    @staticmethod
    def _get_button_width(iter_options):
        """Get width to use for buttons with given options

        Args:
            iter_options (any iterable): options for toggle buttons

        Returns:
            int: width in px to use for buttons with given options
        """
        if not iter_options:
            return 100
        list_lengths = []
        for option in iter_options:
            int_length = 5
            for str_letter in str(option):
                int_length += 8
                if str_letter.isupper():
                    int_length += 4
            list_lengths.append(int_length)
        int_button_width = max(list_lengths)
        int_button_width = max(120, int_button_width)
        int_button_width = min(300, int_button_width)
        return int_button_width


class MultiToggleButtons(BaseToggleButtons):
    """Class to show multi toggle buttons with auto width"""

    _value = tr.Tuple()

    def __init__(self, max_chosen_values=999, **kwargs):
        """Initialize object

        Args:
            max_chosen_values (int): Max buttons can be activated at once
        """
        # Main attributes
        widget_parent = w.SelectMultiple(**kwargs)
        super().__init__(widget_parent, **kwargs)
        self.max_chosen_values = max_chosen_values
        self._tuple_value_types = (list, tuple)
        # Additional (Hidden) attributes
        self.options = kwargs.get("options", [])
        self._dict_but_by_option = OrderedDict()
        self._update_buttons_for_new_options()
        self.value = kwargs.get("value", [])
        self._update_widget_view()
        self._init_update_value()
        self._update_value("bang!!!")

    def _init_update_value(self):
        self.widget_parent.observe(self._update_value, "value")

    def _update_value(self, on_change):
        self._value = self.value

    def _update_widget_view(self):
        """Update view of the widget according to all settings"""
        for str_option in self._dict_but_by_option:
            but_wid = self._dict_but_by_option[str_option]
            if str_option in self.value:
                but_wid.value = True
                but_wid.button_style = "success"
            else:
                but_wid.value = False
                but_wid.button_style = ""

    def _on_click_button_to_choose_option(self, dict_changes):
        """What to do when button to choose options clicked"""
        wid_but = dict_changes["owner"]
        str_value_to_alter = wid_but.description
        list_cur_values = list(self.value)
        if dict_changes["new"]:
            if str_value_to_alter not in list_cur_values:
                list_cur_values += [str_value_to_alter]
                self.value = list_cur_values
        else:
            if str_value_to_alter in list_cur_values:
                list_cur_values.remove(str_value_to_alter)
                self.value = list_cur_values

    def _update_buttons_for_new_options(self):
        """Update buttons if options were changed"""
        list_buttons = []
        self._dict_but_by_option = OrderedDict()
        int_width = self._get_button_width(self.options)
        for str_option in list(self.options):
            but = w.ToggleButton(
                description=str_option, layout={"width": "%dpx" % int_width}
            )
            but.observe(self._on_click_button_to_choose_option, "value")
            self._dict_but_by_option[str_option] = but
            list_buttons.append(but)
        self.children = list_buttons


if __name__ == "__main__":
    from IPython.display import display

    wid = MultiToggleButtons(
        options=[
            str(i)
            + "asdfas;ldfkjas; ldfk;a lksjf;aslfkd asdfa;sldkfjas;ldfk ;LKH ;LKJAS"
            for i in range(20)
        ],
        # max_chosen_values=2,
    )
    display(wid)
# -
if __name__ == "__main__":
    wid.align_horizontal = False
