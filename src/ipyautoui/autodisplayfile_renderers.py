# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

"""
displayfile is used to display certain types of files.
The module lets us preview a file, open a file, and open its directory.

Example:
    ::

        from ipyautoui.constants import load_test_constants
        from ipyautoui.displayfile import DisplayFile, Markdown
        import ipywidgets as widgets

        DIR_FILETYPES = load_test_constants().DIR_FILETYPES

        fpths = list(pathlib.Path(DIR_FILETYPES).glob("*"))

        # single file
        d = AutoDisplay(fpths)
        display(d)

"""
# %run __init__.py
# %load_ext lab_black
# +
import os
import pathlib
import pandas as pd
from IPython.display import display, Markdown, IFrame, clear_output, Image
import json
import ipydatagrid as ipg
import ipywidgets as widgets
import importlib.util
import plotly.io as pio

#  from mf library
try:
    from xlsxtemplater import from_excel
except:
    pass

#  local imports
from ipyautoui.mydocstring_display import display_module_docstring
from ipyautoui._utils import del_matching, display_python_file, frozenmap
from ipyautoui.constants import BUTTON_WIDTH_MIN


# -


# + tags=[]
class PreviewPython:
    """
    pass the class either a filepath or an imported
    module and get a display output of the modules
    docstring with a toggle option to view the code
    """

    def __init__(self, module, preview_script=True, docstring_priority=True):
        self.input = module
        self.preview_script = preview_script
        self.docstring_priority = docstring_priority
        self.out = widgets.Output()
        self.fpth = self._handle_input()
        self._init_form()
        self._init_controls()
        if self.docstring_priority:
            self._show_docstring()
        else:
            self.show_me_the_code.value = True

    def _handle_input(self):
        if str(type(self.input)) == "<class 'module'>":
            fpth = self.input.__file__
        else:
            fpth = self.input
        if os.path.splitext(fpth)[1] != ".py":
            print("{0}: not a python file".format(fpth))
        return fpth

    def _init_form(self):
        self.title = widgets.HTML("")
        self.show_me_the_code = widgets.ToggleButton(
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN)
        )
        self.headerbox = widgets.VBox(
            [widgets.HBox([self.show_me_the_code, self.title])]
        )

        if self.preview_script:
            display(self.headerbox)

    def _init_controls(self):
        self.show_me_the_code.observe(self._show_me_the_code, "value")

    def _update_title(self):
        self.title.value = "👆 {}".format(self.description)

    def _show_docstring(self):
        self.show_me_the_code.icon = "scroll"
        self.show_me_the_code.tooltip = "show the raw python code"
        self.show_me_the_code.button_style = "warning"
        self.description = "show python code"
        self._update_title()
        with self.out:
            clear_output()
            display_module_docstring(self.fpth)

    def _show_me_the_code(self, sender):
        self.show_me_the_code.icon = "book"
        self.show_me_the_code.tooltip = "show the python script documentation"
        self.show_me_the_code.button_style = "info"
        self.description = "show documentation"
        self._update_title()
        with self.out:
            clear_output()
            if self.show_me_the_code.value:
                display_python_file(self.fpth)
            else:
                self._show_docstring()

    def display(self):
        display(self.out)

    def _ipython_display_(self):
        self.display()


# +
def default_grid(df, **kwargs):
    """
    thin wrapper for ipy.DataGrid

    Code:
        _kwargs = {
            'layout':{'width':'100%', 'height':'400px'}
        }
        _kwargs.update(kwargs)  # user overides
        g = ipg.DataGrid(df, **_kwargs)
        return g

    """

    _kwargs = {"layout": {"width": "100%", "height": "400px"}, "auto_fit_columns": True}
    _kwargs.update(kwargs)  # user overides
    g = ipg.DataGrid(df, **_kwargs)
    return g


def preview_csv(path):
    df = del_matching(pd.read_csv(path), "Unnamed")
    return default_grid(df)


def preview_json(path):
    return Markdown(
        f"""
```json
{pathlib.Path(path).read_text()}
```
"""
    )


def check_installed(package_name):
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return False
    else:
        return True


def preview_plotly(path):
    # For illustrative purposes.
    package_name = "plotly"
    if check_installed(package_name):
        return widgets.HTML(package_name + " is not installed")
    else:
        return pio.read_json(path)


def Vega(spec):
    """
    render Vega in jupyterlab
    https://github.com/jupyterlab/jupyterlab/blob/master/examples/vega/vega-extension.ipynb
    """
    bundle = {}
    bundle["application/vnd.vega.v5+json"] = spec
    display(bundle, raw=True)
    # return bundle


def VegaLite(spec):
    """
    render VegaLite in jupyterlab
    https://github.com/jupyterlab/jupyterlab/blob/master/examples/vega/vega-extension.ipynb
    """
    bundle = {}
    bundle["application/vnd.vegalite.v4+json"] = spec
    display(bundle, raw=True)
    # return bundle


def preview_vega(path):
    data = json.loads(pathlib.Path(path).read_text())
    return Vega(data)


def preview_vegalite(path):
    data = json.load(pathlib.Path(path).read_text())
    return VegaLite(data)


def preview_yaml(path):
    return Markdown(
        f"""
```yaml
{pathlib.Path(path).read_text()}
```
"""
    )


def preview_image(path):
    return Image(pathlib.Path(path).read_bytes())


def preview_text(path):
    return Markdown(
        f"""
```
{pathlib.Path(path).read_text()}
```
"""
    )


def preview_markdown(path):
    return Markdown(
        f"""
WARNING: `IMAGES WON'T DISPLAY UNLESS THE MARKDOWN FILE IS IN THE SAME FOLDER AS THIS JUPYTER NOTEBOOK`
{pathlib.Path(path).read_text()}
"""
    )


def preview_pdf(path):
    return IFrame(path, width=1000, height=600)


DEFAULT_FILE_RENDERERS = frozenmap(
    **{
        ".csv": preview_csv,
        ".json": preview_json,
        ".plotly": preview_plotly,
        ".plotly.json": preview_plotly,
        ".vg.json": preview_vega,
        ".vl.json": preview_vegalite,
        ".yaml": preview_yaml,
        ".yml": preview_yaml,
        ".png": preview_image,
        ".jpg": preview_image,
        ".jpeg": preview_image,
        #'.obj': obj_prev, # add ipyvolume viewer?
        ".txt": preview_text,
        ".bat": preview_text,
        ".rst": preview_text,
        "": preview_text,
        ".toml": preview_text,  # TODO: add toml viewer?
        ".md": preview_markdown,
        ".py": PreviewPython,
        ".pdf": preview_pdf,
    }
)
