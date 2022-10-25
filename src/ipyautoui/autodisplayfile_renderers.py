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
from IPython.display import display, Markdown, IFrame, clear_output, Image, HTML
import json
import ipydatagrid as ipg
import ipywidgets as widgets
import importlib.util
import traitlets as tr
import traitlets_paths

#  local imports
from ipyautoui.mydocstring_display import display_module_docstring
from ipyautoui._utils import (
    del_matching,
    display_python_file,
    frozenmap,
    check_installed,
    get_ext,
)
from ipyautoui.constants import BUTTON_WIDTH_MIN
from ipyautoui.custom.showhide import ShowHide

# if check_installed('xlsxtemplater'):
#     from xlsxtemplater import from_excel

if check_installed("plotly"):
    import plotly.io as pio

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


class PreviewExcel(widgets.VBox):
    path = traitlets_paths.Path()
    xl = traitlets.Instance(klass="pandas.ExcelFile")

    def __init__(self, path):
        super().__init__()
        self.path = path

    @traitlets.observe("path")
    def _observe_path(self, change):
        self.xl = pd.ExcelFile(self.path)

    @traitlets.observe("xl")
    def _observe_xl(self, change):
        self.children = [
            ShowHide(title=name, fn_display=lambda: default_grid(self.xl.parse(name)))
            for name in self.xl.sheet_names
        ]


def mdboldstr(string, di):
    """return bold __key__: value from dict"""
    return "__{}__: {}".format(string, di[string])


def mdnorms(di):
    return (
        mdboldstr("ProjectNo", di)
        + " ........ "
        + mdboldstr("Date", di)
        + " ........ "
        + mdboldstr("Author", di)
    )


def mdwildcars(di):
    exclude = [
        "sheet_name",
        "xlsx_params",
        "xlsx_exporter",
        "ProjectNo",
        "Date",
        "Author",
        "df",
        "grid",
    ]
    others = {k: v for k, v in di.items() if k not in exclude}
    mdstr = ""
    for k, v in others.items():
        mdstr = mdstr + "__{}__: {}<br>".format(k, v)
    return mdstr


def mdheader(di):
    return "### {} \n {} <br> {}".format(di["sheet_name"], mdnorms(di), mdwildcars(di))


def xlsxtemplated_display(li):
    """
    displays xlsxtemplated (written using xlsxtemplater) using ipydatagrid
    """
    for l in li:
        l["grid"] = default_grid(l["df"])
        display(Markdown(mdheader(l)))
        display(l["grid"])


def preview_json(path):
    return Markdown(
        f"""
```json
{pathlib.Path(path).read_text()}
```
"""
    )


def preview_plotly(path):
    # For illustrative purposes.
    package_name = "plotly"
    if check_installed(package_name):
        return pio.read_json(path)
    else:
        return widgets.HTML(package_name + " is not installed")


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


def preview_image(path, *args, **kwargs):
    return widgets.Image.from_file(path, *args, **kwargs)


def preview_video(path, *args, **kwargs):
    return widgets.Video.from_file(path, *args, **kwargs)


def preview_audio(path, *args, **kwargs):
    return widgets.Audio.from_file(path, *args, **kwargs)


def preview_text(path):
    return Markdown(
        f"""
```
{pathlib.Path(path).read_text()}
```
"""
    )


def preview_dir(path):
    """preview folder"""
    # TODO: make recursive using AutoDisplay?
    li = path.glob("*")
    make_str = lambda p: f"📁 {p.stem}" if p.is_dir() else f"📄 {p.stem}"
    li = [make_str(l) for l in li]
    return HTML("<br>".join(li))


def preview_text_or_dir(path):
    """display path with ext == "" """
    if path.is_file():
        return preview_text(path)
    else:
        return preview_dir(path)


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
        ".xlsx": PreviewExcel,
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
        ".gif": preview_image,
        ".mp4": preview_video,
        ".mp3": preview_audio,
        #'.obj': obj_prev, # add ipyvolume viewer?
        ".txt": preview_text,
        ".bat": preview_text,
        ".rst": preview_text,
        "": preview_text_or_dir,
        ".toml": preview_text,  # TODO: add toml viewer?
        ".md": preview_markdown,
        ".py": PreviewPython,
        ".pdf": preview_pdf,
    }
)


def handle_compound_ext(ext, map_renderers=DEFAULT_FILE_RENDERERS):
    """_summary_

    Args:
        ext (_type_): _description_
        map_renderers (_type_, optional): _description_. Defaults to DEFAULT_FILE_RENDERERS.

    Returns:
        _type_: _description_
    """
    li_ext = ext.split(".")
    if ext in list(map_renderers.keys()):
        return ext
    elif len(li_ext) > 2:
        # it is a compound filetype when the compound didn't match
        # so return main ext
        return "." + li_ext[-1]
    else:
        return ext


def render_file(path: pathlib.Path, map_renderers=DEFAULT_FILE_RENDERERS):
    """simple file renderer.

    Note:
        this function is not used by AutoDisplay, but is provided here for simple
        API functionality

    Args:
        path (pathlib.Path):
        map_renderers (_type_, optional): _description_. Defaults to DEFAULT_FILE_RENDERERS.

    Returns:
        something to display
    """
    # note: this isn't used by AutoDisplay
    path = pathlib.Path(path)
    ext = get_ext(path)
    ext = handle_compound_ext(ext)
    return map_renderers[ext](path)
