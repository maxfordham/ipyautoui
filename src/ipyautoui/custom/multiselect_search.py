# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

"""
multiselect dropdown widget definition. TODO: integrate with ipyautoui

Reference:
    https://gist.github.com/MattJBritton/9dc26109acb4dfe17820cf72d82f1e6f
        

"""
# %run ../__init__.py
import sys
import ipywidgets as widgets
import requests
import random

# +



class MultiSelectSearch:
    """
    multi-checkbox select widget with search 
    
    Reference:
        multi-select widget:
            https://gist.github.com/MattJBritton/9dc26109acb4dfe17820cf72d82f1e6f
    """
    def __init__(self, options):
        self.options_dict = {
            x: widgets.Checkbox(
                description=x, 
                value=False,
                style={"description_width":"0px"}
            ) for x in options
        }
        
        self.ui = self.multi_checkbox_widget(self.options_dict)
        self.out = widgets.interactive_output(self.f, self.options_dict)
    
    def display(self):
        display(widgets.HBox([self.ui, self.out]))
    
    def _ipython_display_(self):
        self.display()
        
    def f(self, **args):
        self.value = [key for key, value in args.items() if value]
        display(self.value)
    
    def multi_checkbox_widget(self,options_dict):
        """ Widget with a search field and lots of checkboxes """
        search_widget = widgets.Text()
        output_widget = widgets.Output()
        options = [x for x in options_dict.values()]
        options_layout = widgets.Layout(
            overflow='auto',
            border='1px solid black',
            width='400px',
            height='300px',
            flex_flow='column',
            display='flex'
        )
        options_widget = widgets.VBox(options, layout=options_layout)
        multi_select = widgets.VBox([search_widget, options_widget])

        @output_widget.capture()
        def on_checkbox_change(change):
            selected_recipe = change["owner"].description
            options_widget.children = sorted([x for x in options_widget.children], key = lambda x: x.value, reverse = True)

        for checkbox in options:
            checkbox.observe(on_checkbox_change, names="value")

        # Wire the search field to the checkboxes
        @output_widget.capture()
        def on_text_change(change):
            search_input = change['new']
            if search_input == '':
                # Reset search field
                new_options = sorted(options, key = lambda x: x.value, reverse = True)
            else:
                # Filter by search field using difflib.
                close_matches = [x for x in list(options_dict.keys()) if str.lower(search_input.strip('')) in str.lower(x)]
                new_options = sorted(
                    [x for x in options if x.description in close_matches], 
                    key = lambda x: x.value, reverse = True
                ) #[options_dict[x] for x in close_matches]
            options_widget.children = new_options

        search_widget.observe(on_text_change, names='value')
        display(output_widget)
        return multi_select

if __name__ == "__main__":
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


