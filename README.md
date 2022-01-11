---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.3
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# ipyautoui

wrapper that sits on top of ipywidgets and other ipy widget libraries to template / automate the creation of widget forms. Uses pydantic to create defined data-container and serialisation to JSON. Includes example patterns for adding new custom widgets.

+++

## Create a UI object

ipyautoui creates a row of widgets with a: `name`, `value` and `label`. The `value` is interpreted by the WidgetRowBase class and a widget is widget type is guess by the type of the value and the `kwargs` that can also be passed when initialising the widget.

```{code-cell} ipython3
# TODO: refer to ipyfilechooser for inspiration for README.md
```

```{code-cell} ipython3
import sys
sys.path.append('src')
from ipyautoui.autoui import AutoUi

?AutoUi
```

```{code-cell} ipython3
rows = [
    {'value': 1, 'name':'integer'},
    {'value': 'string'}, 
    {'value': 1, 'kwargs': {'min':0, 'max':4}}
]

aui = AutoUiBase(rows = rows)
ui = AutoUi(aui)
ui
```

```{code-cell} ipython3
# AutoUi class adds the widget attribute
# it uses traitlets to ensure that if the widget value
# changes the ui.value attribute also changes with it
display(ui.rows[0].widget)
print(ui.rows[0].widget.value)
ui.rows[0].widget.value = 2
ui.rows[0].value
```

## Output / transport data from UI

```{code-cell} ipython3
## using Pydantic data serialisation amd config option introduced in v1.8.3,
# the JSON inconpatible attributes are removed
# when the widget is written to dict or JSON. 
ui.dict()
```

## Reload data back into UI

the `autoui_type` saves a class string defining what widget should be used. This is converted to the object using importlib.

```{code-cell} ipython3
#  importlib is used to create the widget from the `autoui_type` string characteristic
aui = AutoUiBase(**ui.dict())
AutoUi(aui)
```

## Create custom UI object rows

This library mainly relies on ipywidgets, but other libraries can also be used. The AutoUi widget uses traitlets to watch when the `widget.value` changes, wrappers can be made around other widget libraries to allow this behaviour. 

In this way pandas dataframes using ipydatagrid can also be used.

(See `ipyautoui.custom_widgets` for more examples.

```{code-cell} ipython3
import pandas as pd
rows.append(
    {'name':'pandas', 'value': pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}), 'label': 'example of a custom widget'}
)
```

```{code-cell} ipython3
aui = AutoUiBase(rows = rows)
ui = AutoUi(aui)
ui
```

## Write to file

```{code-cell} ipython3

```
