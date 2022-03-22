# ipyautoui

A high-level wrapper library that sits on top of [__ipywidgets__](https://github.com/jupyter-widgets/ipywidgets) (and other ipy- widget libraries), [__pydantic__](https://github.com/samuelcolvin/pydantic/) and Jupycter rich display system to template and automate the creation of widget forms / user-interfaces. The core user-facing classes in this library are __AutoUi__ and __DisplayFiles__:
```python
from ipyautoui import AutoUi, DisplayFiles
```
## How it works: 

- Make a pydantic model (or json schema) that defines the UI
- Pass the model to `AutoUi` to generate an user-interface
- Save the UI fields to file 
- Assign a compound-json filetype to the schema and generate `DisplayFiles` rendererer
- Use `DisplayFiles` to display the json file using the AutoUi interface

## Dependencies

This package intends to be high-level, and unifies many other ipy- libraries under a simple and familliar API. 
Core widget dependencies include: 
- ipywidgets
- ipydatagrid
- ipyfilechooser
- ipyvue
- ipyvuetify
- vuetify-jsonschema-form
- Altair (for viewing `.vg.json` files)
- Plotly (for viewing `.plotly.json` files)


## AutoUi

- AutoUi uses [__pydantic__](https://github.com/samuelcolvin/pydantic/) to define the schema of User Input form, and then infers the widget to use based on type and user-directives
- Within the core package there are also custom high-level widgets (e.g. Array of items), as well as integration's with other popular widget libraries (e.g. ipydatagrid, ipyfilechooser): this both adds useful functionality not provided within the lower-level widget libraries as well as providing a template for how to extend the core functionality of ipyautoui to suit more specific use-cases. 
- ipyautoui handles observing the values of interface items, and maintains a stateful and validated `.value` parameter for the whole user input form.  
- TODO: AutoUi also allows the user to specify the usage of [__ipyvuetify__](https://github.com/widgetti/ipyvuetify) and [__vuetify-jsonschema-form__](https://github.com/koumoul-dev/vuetify-jsonschema-form)
    - __note__. this is the recommended approach for simple and generic input forms. Where custom UI objects are required these can be built using the ipyautoui core library. 


```python
from pydantic import BaseModel, Field
from ipyautoui import AutoUi

class LineGraph(BaseModel):
    """parameters to define a simple `y=m*x + c` line graph"""
    title: str = Field(default='line equation', description='add chart title here')
    m: float = Field(default=2, description='gradient')
    c: float = Field(default=5, description='intercept')
    x_range: tuple[int, int] = Field(default=(0,5), ge=0, le=50, description='x-range for chart')
    y_range: tuple[int, int] = Field(default=(0,5), ge=0, le=50, description='y-range for chart')
    
lg = LineGraph()
ui = AutoUi(pydantic_obj=lg)
ui
```
![](images/autoui-linegraph.png)

```python

ui.value  # there is a `value` trait that is always kept in-sync with the widget input form
# {'title': 'line equation',
#  'm': 2,
#  'c': 5,
#  'x_range': (0, 5),
#  'y_range': (0, 5)}

#  methods / stored values
ui.file #  file data to .json file
ui.value #  input form value dict
ui.pydantic_obj #  input form pydantic model (note. value is created from this on_change)
AutoUi.create_displayfile_renderer #  creates a json-serializable pointer 
AutoUi.parse_file #  init ui with data from .json file
```

__Current Limations__: 

- Doesn't support nested objects or arrays. Coming soon... 

## DisplayFiles 

`(TODO: name change to display, facilitating display of database data?)`

- DisplayFiles uses Jupyter's rich display system and large ecosystem of 3rd party packages to create a simple and unified display wrapper to various filetypes.
- The renderer for a given file is inferred from the file extension. 
     - TODO: where the datasource is not a file, the extension is a mapping code that maps a renderer to the datastructure of the data. 
- Custom renderer's can be passed to `DisplayFiles` allowing it to display user-defined filetypes (or compound extension filetypes)




## Development installation

For a development installation (requires JupyterLab (version >= 3), yarn, and mamba.):

```
$ git clone https://github.com/jgunstone/ipyautoui
$ cd ipyautoui
$ mamba env create --file environment-dev.yml
```
