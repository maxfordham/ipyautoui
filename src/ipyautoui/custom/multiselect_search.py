# +
"""
multiselect dropdown widget definition. TODO: integrate with ipyautoui

Reference:
    https://gist.github.com/MattJBritton/9dc26109acb4dfe17820cf72d82f1e6f
        

"""
import ipywidgets as w
import traitlets as tr

BUTTON_WIDTH_MIN = "50px"


# +
class MultiSelectSearch(w.VBox):
    """
    multi-checkbox select widget with search

    Reference:
        multi-select widget:
            https://gist.github.com/MattJBritton/9dc26109acb4dfe17820cf72d82f1e6f
    """

    _options = tr.List(default_value=[])
    _value = tr.List(default_value=[])

    def __init__(self, options=[], value=[]):
        super().__init__()
        self.check_all = w.Button(
            icon="check-square-o",
            tooltip="Check all",
            button_style="success",
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.uncheck_all = w.Button(
            icon="square-o",
            tooltip="Uncheck all",
            button_style="warning",
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.delete = w.Button(
            icon="trash-alt",
            tooltip="Deleted checked items",
            button_style="danger",
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.options = options
        self.value = value
        self._init_controls()

    def _init_controls(self):
        self.check_all.on_click(self._check_all)
        self.uncheck_all.on_click(self._uncheck_all)
        self.delete.on_click(self._delete_checked)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        self._options = value
        self.options_dict = {
            x: w.Checkbox(
                description=x, value=False, style={"description_width": "0px"}
            )
            for x in value
        }
        self.ui = self.multi_checkbox_widget(self.options_dict)
        self.children = [self.ui]

    @property
    def value(self):  # FIXME: don't set value on retrieval in case it was changed
        self._value = [
            name
            for name, checkbox in self.options_dict.items()
            if checkbox.value is True
        ]
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        for name in value:
            self.options_dict[name].value = True

    def _check_all(self, onchange):
        for name, checkbox in self.options_dict.items():
            checkbox.value = True

    def _uncheck_all(self, onchange):
        for name, checkbox in reversed(self.options_dict.items()):
            checkbox.value = False

    def _delete_checked(self, onchange):
        self.options = [option for option in self.options if option not in self.value]

    def multi_checkbox_widget(self, options_dict):
        """Widget with a search field and lots of checkboxes"""
        search_widget = w.Text()
        output_widget = w.Output()
        options = [x for x in options_dict.values()]
        options_layout = w.Layout(
            overflow="auto",
            border="1px solid black",
            width="470px",
            height="300px",
            flex_flow="column",
            display="flex",
        )
        options_widget = w.VBox(options, layout=options_layout)
        multi_select = w.VBox(
            [
                w.HBox([search_widget, self.check_all, self.uncheck_all, self.delete]),
                options_widget,
            ]
        )

        @output_widget.capture()
        def on_checkbox_change(change):
            selected_recipe = change["owner"].description
            options_widget.children = sorted(
                [x for x in options_widget.children],
                key=lambda x: x.value,
                reverse=True,
            )

        for checkbox in options:
            checkbox.observe(on_checkbox_change, names="value")

        # Wire the search field to the checkboxes
        @output_widget.capture()
        def on_text_change(change):
            search_input = change["new"]
            if search_input == "":
                # Reset search field
                new_options = sorted(options, key=lambda x: x.value, reverse=True)
            else:
                # Filter by search field using difflib.
                close_matches = [
                    x
                    for x in list(options_dict.keys())
                    if str.lower(search_input.strip("")) in str.lower(x)
                ]
                new_options = sorted(
                    [x for x in options if x.description in close_matches],
                    key=lambda x: x.value,
                    reverse=True,
                )  # [options_dict[x] for x in close_matches]
            options_widget.children = new_options

        search_widget.observe(on_text_change, names="value")
        return multi_select


if __name__ == "__main__":
    from IPython.display import display

    words = """
a
AAA
AAAS
aardvark
Aarhus
Aaron
ABA
Ababa
aback
abacus
abalone
abandon
abase
abash
abate
abbas
abbe
abbey
abbot
Abbott
abbreviate
abc
abdicate
abdomen
abdominal
abduct
Abe
abed
Abel
    """
    words = set([word.lower() for word in words.splitlines()])
    descriptions = list(words)[:10]

    m = MultiSelectSearch(options=descriptions)
    display(m)
# -
