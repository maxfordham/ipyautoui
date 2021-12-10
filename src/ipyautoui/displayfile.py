# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %run __init__.py

# +
import pathlib
import os
import subprocess
import pathlib
import pandas as pd
import numpy as np
from IPython.display import display, JSON, Markdown, HTML, IFrame, clear_output, Image
import time
from markdown import markdown
import copy
from dataclasses import dataclass, asdict, field
from dacite import from_dict
from typing import List, Dict, Callable, Type
import typing
import enum
import getpass
import json

import ipydatagrid as ipg
import ipywidgets as widgets
from halo import HaloNotebook
import plotly.io as pio

#  from mf library
try: 
    from mf_file_utilities import go as open_file
except:
    def open_file(path):
        subprocess.call(['open', path])
try:      
    from xlsxtemplater import from_excel
except:
    pass

#  local imports
from ipyautoui.mydocstring_display import display_module_docstring
from ipyautoui._utils import del_matching, md_fromfile, display_python_file, read_json, read_yaml, read_txt
#from ipyrun._runconfig import Output, Outputs, File
from ipyautoui.constants import BUTTON_WIDTH_MIN, BUTTON_HEIGHT_MIN


# +
#  NOT IN USE - need a way to display pdf's!
#  https://github.com/voila-dashboards/voila/issues/659
#  i think this is resolved... need to make sure the path given is relative to the notebook... 

# def served_pdf():
#     value=r'<iframe width="500" height="600" src="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf" frameborder="1" allowfullscreen></iframe>'
#     myhtml =widgets.HTML(
#         value=value,
#         placeholder='Some HTML',
#         description='Some HTML',
#     )
#     display(myhtml)
    
# def local_pdf():
#     value=r'<iframe width="500" height="600" src="../test_filetypes/eg_pdf.pdf" frameborder="1" allowfullscreen></iframe>'
#     myhtml =widgets.HTML(
#         value=value,
#         placeholder='Some HTML',
#         description='Some HTML',
#     )
#     display(myhtml)
    
# def fromfile_pdf():
#     value=r'<iframe width="500" height="600" src="file:///mnt/c/engDev/git_mf/ipyrun/test_filetypes/eg_pdf.pdf" frameborder="1" allowfullscreen></iframe>'
#     myhtml =widgets.HTML(
#         value=value,
#         placeholder='Some HTML',
#         description='Some HTML',
#     )
#     display(myhtml)

#served_pdf()
#local_pdf()
#fromfile_pdf()

# +
def _markdown(value='_Markdown_',
              **kwargs):
    """
    a simple template for markdown text input that templates required input
    fields. additional user defined fields can be added as kwargs
    """
    _kwargs = {}
    _kwargs['value'] = markdown(value)  # required field
    _kwargs.update(kwargs)  # user overides
    return widgets.HTML(**_kwargs)

def mdboldstr(string, di):
    return '__{}__: {}'.format(string,di[string])

def mdnorms(di):
    return mdboldstr('ProjectNo', di) + ' ........ ' + mdboldstr('Date', di) + ' ........ ' + mdboldstr('Author', di)

def mdwildcars(di):
    exclude = ['sheet_name', 'xlsx_params', 'xlsx_exporter', 'ProjectNo', 'Date', 'Author', 'df', 'grid']
    others = {k:v for k,v in di.items() if k not in exclude}
    mdstr = ''
    for k, v in others.items():
        mdstr = mdstr + '__{}__: {}<br>'.format(k,v) 
    return mdstr

def mdheader(di):
    return '### {} \n {} <br> {}'.format(
        di['sheet_name'], mdnorms(di), mdwildcars(di)
    )

def xlsxtemplated_display(li):
    """
    displays xlsxtemplated (written using xlsxtemplater) using ipydatagrid
    """
    for l in li:
        l['grid'] = default_grid(l['df'])
        display(Markdown(mdheader(l)))
        display(l['grid'])
#  string = 'ProjectNo'
#  mdheader(di)


# -

def display_button_styles():
    """displays default ipywidget button styles"""
    styles = ['primary', 'success', 'info', 'warning', 'danger']
    for s in styles:
        b = widgets.ToggleButton(description=s, button_style=s)
        t = _markdown('```widgets.ToggleButton(description="{}", button_style="{}")```'.format(s,s))
        display(widgets.HBox([b,t]))
if __name__ == "__main__":
    display_button_styles()


# +
def get_ext(fpth):
    """get file extension including compound json files"""
    return ''.join(pathlib.Path(fpth).suffixes)

def Vega(spec):
    """
    render Vega in jupyterlab
    https://github.com/jupyterlab/jupyterlab/blob/master/examples/vega/vega-extension.ipynb
    """
    bundle = {}
    bundle['application/vnd.vega.v5+json'] = spec
    display(bundle, raw=True);

def VegaLite(spec):
    """
    render VegaLite in jupyterlab
    https://github.com/jupyterlab/jupyterlab/blob/master/examples/vega/vega-extension.ipynb
    """
    bundle = {}
    bundle['application/vnd.vegalite.v4+json'] = spec
    display(bundle, raw=True);


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

    _kwargs = {
        'layout':{'width':'100%', 'height':'400px'},
        'auto_fit_columns': True
    }
    _kwargs.update(kwargs)  # user overides
    g = ipg.DataGrid(df, **_kwargs)
    return g

# if __name__ == "__main__":
#     df = pd.DataFrame.from_dict({'a':['a','b'],'b':['a','b']})
#     display(default_grid(df))


# +
class PreviewPy():
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
        if os.path.splitext(fpth)[1] != '.py':
            print('{0}: not a python file'.format(fpth))
        return fpth

    def _init_form(self):
        self.script_name = os.path.splitext(os.path.basename(self.fpth))[0]
        self.title = widgets.HTML('')
        self.show_fpth = _markdown('``` {} ```'.format(self.fpth))          
        self.show_me_the_code = widgets.ToggleButton(
                              layout=widgets.Layout(width=BUTTON_WIDTH_MIN)
        )
        self.headerbox = widgets.VBox([widgets.HBox([self.show_me_the_code, self.title]), self.show_fpth])
                               
        if self.preview_script:
            display(self.headerbox)
            
    def _init_controls(self):
        self.show_me_the_code.observe(self._show_me_the_code, 'value')
    
    def _update_title(self):
        self.title.value = '<b>{}</b>: {}'.format(self.script_name, self.description)

    def _show_docstring(self):
        self.show_me_the_code.icon='scroll'
        self.show_me_the_code.tooltip='show the raw python code'
        self.show_me_the_code.button_style='warning'
        self.description = 'script documentation'
        self._update_title()
        with self.out:
            clear_output()
            display_module_docstring(self.fpth)

    def _show_me_the_code(self, sender):
        self.show_me_the_code.icon='book'
        self.show_me_the_code.tooltip='show the python script documentation'
        self.show_me_the_code.button_style='info'
        self.description = 'python script'
        self._update_title()
        with self.out:
            clear_output()
            if self.show_me_the_code.value:
                display(display_python_file(self.fpth))
            else:
                self._show_docstring()

    def display(self):
        display(self.out)

    def _ipython_display_(self):
        self.display()

if __name__ == "__main__":
    fpth = 'test_schema.py'
    display(PreviewPy(fpth)) 

# +


def pdf_prev(fpth):
    display(IFrame(fpth, width=1000, height=600))

def csv_prev(fpth):
    """
    previes dataframe using the awesome ipydatagrid

    Reference:
        ipydatagrid
    """
    data = del_matching(pd.read_csv(fpth),'Unnamed')
    try:
        g = default_grid(data)
        display(g)
    except:
        display(data.style)

def vegajson_prev(fpth):  # TODO: not working. fix!
    """display a plotly json file"""
    with open(fpth, 'r', encoding='utf8') as f:
        json_file = json.load(f)
    display(Vega(json_file))

def vegalitejson_prev(fpth):  # TODO: not working. fix!
    """display a plotly json file"""
    with open(fpth, 'r', encoding='utf8') as f:
        json_file = json.load(f)
    display(VegaLite(json_file))

def plotlyjson_prev(fpth):
    """display a plotly json file"""
    if type(fpth) is not str:
        fpth = str(fpth)
    display(pio.read_json(fpth))

def ipyuijson_prev(fpth):
    print('add here!')

def json_prev(fpth):
    display(JSON(read_json(fpth)))

def yaml_prev(fpth):
    data = read_yaml(fpth)
    display(JSON(data))

def img_prev(fpth):
    display(Image(fpth))

def md_prev(fpth):
    display(Markdown("`IMAGES WON'T DISPLAY UNLESS THE MARKDOWN FILE IS IN THE SAME FOLDER AS THIS JUPYTER NOTEBOOK`"))
    md_fromfile(fpth)

def py_prev(fpth):
    """
    pass the fpth of a python file and get a
    rendered view of the code.
    """
    p = PreviewPy(fpth)
    display(p)

def txt_prev(fpth):
    display(Markdown("```{}```".format(read_txt(fpth, read_lines=False))))

def xl_prev(fpth):
    """display excel. if xlsxtemplated display as Grid, otherwise as _open_option"""
    li = from_excel(fpth)
    if li is not None:
        xlsxtemplated_display(li)
        return True
    else:
        return False
        #self._open_option()


# +
# fpth = pathlib.Path('/mnt/c/engDev/git_mf/ipyautoui/tests/filetypes/eg_vega_tree-layout.vg.json')
# fpth = '/mnt/c/engDev/git_mf/ipyautoui/tests/filetypes/eg_vega_tree-layout.vg.json'
# vegajson_prev(fpth)

# + tags=[]

def string_of_time(t):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))

def st_mtime_string(path):
    try: 
        t = path.stat().st_mtime
        return string_of_time(t)
    except:
        return '####-##-## ##:##:##'

# Enum for size units
class SIZE_UNIT(enum.Enum):
    BYTES = 1
    KB = 2
    MB = 3
    GB = 4
    
def convert_unit(size_in_bytes, unit):
    """ Convert the size from bytes to other units like KB, MB or GB"""
    if unit == SIZE_UNIT.KB:
        return size_in_bytes/1024
    elif unit == SIZE_UNIT.MB:
        return size_in_bytes/(1024*1024)
    elif unit == SIZE_UNIT.GB:
        return size_in_bytes/(1024*1024*1024)
    else:
        return np.round(size_in_bytes,2)
    
def format_number(number, sigfigs=3):
    return '{:g}'.format(float('{:.{p}g}'.format(number, p=sigfigs)))

def get_file_size(path:pathlib.Path, size_type = SIZE_UNIT.MB, sigfigs=3):
    """ Get file in size in given unit like KB, MB or GB"""
    if path.is_file():
        return format_number(convert_unit(path.stat().st_size, size_type))
    else:
        return '-'
    
def get_file_data(path):
    return [
        widgets.HTML(f' | <b>{getpass.getuser()}</b>'), 
        widgets.HTML(f' | <i>{st_mtime_string(path)}</i>'),
        widgets.HTML(f' | <i>{get_file_size(path)} MB</i>'),
    ]

def open_ui(fpth: str):
    """
    creates open file and open folder buttons
    fpth used for building tooltip
    
    Args:
        fpth
    
    Returns:
        openpreview
        openfile
        openfolder
    """
    if type(fpth) != pathlib.Path:
        fpth = pathlib.Path(fpth)
    isfile = widgets.Button(disabled=True,layout=widgets.Layout(width=BUTTON_WIDTH_MIN, height=BUTTON_HEIGHT_MIN))
    openpreview = widgets.ToggleButton(
        icon='eye', 
        layout=widgets.Layout(width=BUTTON_WIDTH_MIN, height=BUTTON_HEIGHT_MIN),
        tooltip='preview file: {0}'.format(fpth),
        style={'font_weight': 'bold','button_color':None}) 
    openfile = widgets.Button(
        layout=widgets.Layout(width=BUTTON_WIDTH_MIN, height=BUTTON_HEIGHT_MIN),
        icon='fa-file',
        tooltip='open file: {0}'.format(fpth),
        style={'font_weight': 'bold','button_color':None})   #,'button_color':'white'
    openfolder = widgets.Button(
        #description='+', 
        layout=widgets.Layout(width=BUTTON_WIDTH_MIN, height=BUTTON_HEIGHT_MIN),#,height='20px'
        icon='fa-folder',
        tooltip='open folder: {0}'.format(os.path.dirname(fpth)),
        style={'font_weight': 'bold','button_color':None}) #,'button_color':'LightYellow'
    filename = widgets.HTML(
        '<b>{0}</b>'.format(fpth.name),layout=widgets.Layout(justify_items='center'))   
    data = widgets.HBox(layout=widgets.Layout(justify_items='center'))
    data.children = get_file_data(fpth) 
    return isfile, openpreview, openfile, openfolder, filename, data

    
class UiFile():
    """generic ipywidget file object"""
    def __init__(self, path, save=True):
        self.path = pathlib.Path(path)
        self._init_form()
        self._update_file()
        
    def _init_form(self):
        self.isfile, self.openpreview, self.openfile, self.openfolder, self.filename, self.data = open_ui(self.path)
        self.box_isfile = widgets.HBox([self.isfile],layout=widgets.Layout(width='40px'))
        self.box_file = widgets.HBox([self.box_isfile, self.openpreview, self.openfile, self.openfolder, self.filename, self.data])
    
    def _update_file(self):
        #self.spinner.stop()
        #self.box_isfile.children = [self.isfile]
        if self.path.is_file():
            self.isfile.icon='fa-check'
            self.isfile.style={'button_color':'SpringGreen'}
        else:
            self.isfile.icon='fa-times'
            self.isfile.style={'button_color':'red'}
        self.data.value = get_file_data(self.path)
        
    def _activate_waiting(self, wait_time=None):
        self.isfile.icon='fa-circle'
        self.isfile.style={'button_color':'yellow'}
#         spinner = HaloNotebook(animation='marquee', spinner='dots')
#         with spinner.output:
#             spinner.start()
#             self.box_isfile.children = [spinner.output]
    
        
    def display(self):
        display(self.box_file) 
        
    def _ipython_display_(self):
        self.display()
        
default_file_renderers = {
        '.csv': csv_prev,
        '.json': json_prev,
        '.plotly': plotlyjson_prev,
        '.plotly.json': plotlyjson_prev,
        '.vg.json': vegajson_prev,
        '.vl.json': vegalitejson_prev,
        '.ipyui.json': ipyuijson_prev,
        '.yaml': yaml_prev,
        '.yml': yaml_prev,
        '.png': img_prev,
        '.jpg': img_prev,
        '.jpeg': img_prev,
        #'.obj': obj_prev, # add ipyvolume viewer? 
        '.txt': txt_prev,
        '.md': md_prev,
        '.py': py_prev,
        '.pdf': pdf_prev,
    }

def preview_path(path: typing.Union[str, pathlib.Path],
                 default_file_renderers: Dict[str, Callable] = default_file_renderers,
                 user_file_renderers: Dict[str, Callable] = None):
    if user_file_renderers is None:
        user_file_renderers = {}
    path = pathlib.Path(path)
    ext = get_ext(path)
    ext_map = {**default_file_renderers, **user_file_renderers}
    if ext not in list(ext_map.keys()):
        display(Markdown('cannot preview this file type'));
    else:
        fn = ext_map[ext]
        fn(path)

class DisplayFile():
    """
    displays the contents of a file in the notebook.
    """
    def __init__(self,
                 path: typing.Union[str, pathlib.Path],
                 default_file_renderers: Dict[str, Callable] = default_file_renderers,
                 user_file_renderers: Dict[str, Callable] = None,
                 newroot=pathlib.PureWindowsPath('J:/'),
                 auto_open: bool=False
                ):
        """
        comes with the following default renderers:
            default_file_renderers = {
                    '.csv': csv_prev,
                    '.json': json_prev,
                    '.plotly': plotlyjson_prev,
                    '.plotly.json': plotlyjson_prev,
                    '.vg.json': vegajson_prev,
                    '.vl.json': vegalitejson_prev,
                    '.ipyui.json': ipyuijson_prev,
                    '.yaml': yaml_prev,
                    '.yml': yaml_prev,
                    '.png': img_prev,
                    '.jpg': img_prev,
                    '.jpeg': img_prev,
                    #'.obj': obj_prev, # add ipyvolume viewer? 
                    '.txt': txt_prev,
                    '.md': md_prev,
                    '.py': py_prev,
                    '.pdf': pdf_prev,
                }
        user_file_renderers can be passed to class provided they have the correct
        dict format:
            user_file_renderers = {'.ext': myrenderer}
        notice that the class allows for "compound" filetypes, especially useful for .json files
        if you want to display the data in a specific way. 
        
        Args:
            fpth (str): filepath to display
            user_file_renderers: Dict[str, Callable] = None : user defined file renderers to extend
                the class
                
        Usage:
            fpth = 'default_config.yaml'
            DisplayFile(fpth).preview_fpth()
        
        How to extend:
            if you want to update the class definition for a compound filetype that you have created, 
            you can do so using functools as follows:
            ```
                DisplayFile('default_config.test.yaml').preview_fpth()  # '.test.yaml' ext doesn't exist so renderer defaults to .yaml
                
                import functools
                user_file_renderers = {'.test.yaml': txt_prev}
                DisplayFile = functools.partial(DisplayFile, user_file_renderers=user_file_renderers)
                DisplayFile('default_config.test.yaml').preview_fpth()  # display yaml file as txt_prev renderer
            ```
        """
        self.ui_file = UiFile(path)
        self.fdir = self.ui_file.path.parent
        self.ext = get_ext(self.ui_file.path)
        self.newroot = newroot
        self.out_caller = widgets.Output()
        self.out = widgets.Output()
        self.default_file_renderers = default_file_renderers
        self.user_file_renderers = user_file_renderers
        self._open_form()
        self._init_controls()
        if auto_open: 
            self.ui_file.openpreview.value = True
            
    @property
    def path(self):
        return self.ui_file.path
            
    def _activate_waiting(self):
        self.ui_file._activate_waiting()
        
    def _update_file(self):
        self.ui_file._update_file()

    def preview_path(self):
        preview_path(self.ui_file.path, 
                     default_file_renderers=self.default_file_renderers,
                     user_file_renderers=self.user_file_renderers)
        
        
    def _open_form(self):
        self.open_ui = widgets.VBox([self.ui_file.box_file, self.out_caller, self.out])
        
    def _init_controls(self):
        self.ui_file.openfile.on_click(self._openfile)
        self.ui_file.openfolder.on_click(self._openfolder)
        self.ui_file.openpreview.observe(self._openpreview, names='value')

    def _open_option(self, sender):
        self._open_form()
        self._init_controls()
        display(self.open_form)
                                    
    def _openpreview(self, onchange):
        if self.ui_file.openpreview.value:
            self.ui_file.openpreview.icon ='eye-slash'
            with self.out:
                self.preview_path()
        else:
            self.ui_file.openpreview.icon = 'eye'
            with self.out:
                clear_output()
                                    
    def _openfile(self, sender):
        with self.out_caller:
            clear_output()
            open_file(self.ui_file.path,newroot=self.newroot)
            time.sleep(5)
            clear_output()
        
    def _openfolder(self, sender):
        with self.out_caller:
            clear_output()
            open_file(self.fdir,newroot=self.newroot)
            time.sleep(5)
            clear_output()
            
    def display(self):
        display(self.open_ui) 
        
    def _ipython_display_(self):
        self.display()
            
# if __name__ == "__main__":
#     fpth = 'test_schema.py'
#     d = DisplayFile(fpth, auto_open=True)
#     display(d)
# +
class DisplayFiles():
    def __init__(self, 
                 paths: typing.List[pathlib.Path], 
                 default_file_renderers: Dict[str, Callable] = default_file_renderers,
                 user_file_renderers: Dict[str, Callable] = None,
                 newroot=pathlib.PureWindowsPath('J:/'),
                 auto_open: bool=False, # TODO - add possibility to open only certain items...
                ):
        self.display_files = [DisplayFile(p, auto_open=auto_open, user_file_renderers=user_file_renderers, default_file_renderers=default_file_renderers) for p in paths]
        self._init_form()
        
    def _init_form(self):
        self.box_files = widgets.VBox([d.open_ui for d in self.display_files])
      
    @property
    def paths(self):
        return [d.path for d in self.display_files]
        
    def display(self):
        display(self.box_files) 
        
    def _ipython_display_(self):
        self.display()
        
    def _activate_waiting(self):
        [d.ui_file._activate_waiting() for d in self.display_files]
        
    def _update_files(self):
        [d.ui_file._update_file() for d in self.display_files]
        
# if __name__ == "__main__":
#     fpth1 = fpth
#     files = DisplayFiles([fpth, fpth1])
#     display(files)


# -

if __name__ =='__main__':
    # NOTE FOR FUTURE:
    # the below can be used to make documentation that looks at all functions or classes
    # rather than only the module level docstring. this would be an update to the PreviewPy class
    # +
    #from inspect import getmembers, isfunction, isclass
    #from mf_modules import mydocstring_display

    #functions_list = [o for o in getmembers(mydocstring_display) if isfunction(o[1])]
    #class_list = [o for o in getmembers(mydocstring_display) if isclass(o[1])]
    #functions_list
    #class_list
    # -
    from constants import load_test_constants
    DIR_FILETYPES = load_test_constants().DIR_FILETYPES

    fpths = list(pathlib.Path(DIR_FILETYPES).glob('*'))
    #fpths = [os.path.join(rel,  fpth for fpth in fpths ]

    # single file
    d0 = DisplayFile(fpths[0])
    display(Markdown('### Example0'))
    display(Markdown('''display single file'''))
    display(d0.preview_path())
    display(Markdown('---'))
    display(Markdown(''))
    
    # single Output
    #o0 = Output(fpth=fpths[0])
    p0 = DisplayFile(fpths[0])
    display(Markdown('### Example5'))
    display(Markdown('''display single Output'''))
    display(p0)
    display(Markdown('---'))
    display(Markdown(''))
    
    # single Output side by side
    #o0 = Output(fpth=fpths[0])
    p0 = DisplayFile(fpths[0])
    display(Markdown('### Example5'))
    display(Markdown('''display single Output'''))
    out1 = widgets.Output()
    out2 = widgets.Output()
    with out1: 
        display(p0)
    with out2: 
        display(p0)
    display(widgets.HBox([out1, out2], layout=widgets.Layout(justify_content='space-around')))
    display(Markdown('---'))
    display(Markdown(''))
    
    # multiple Outputs
    # outputs = [Output(f) for f in fpths]
    p1 = DisplayFiles(fpths)
    display(Markdown('### Example6'))
    display(Markdown('''display multiple Outputs'''))
    display(p1)
    display(Markdown('---'))
    display(Markdown(''))

if __name__ == "__main__":
    p1._activate_waiting()
    time.sleep(2)
    p1._update_files()

if __name__ == "__main__":
    display(Markdown('### Example7'))
    display(Markdown('''extend standard supported filetypes'''))
    #import
    from ipyautoui.test_schema import TestAutoLogic
    from ipyautoui.autoui import AutoUi, AutoUiConfig
    from ipyautoui.constants import load_test_constants
    tests_constants = load_test_constants()
    config_ui = AutoUiConfig(ext='.aui.json', pydantic_model=TestAutoLogic)
    TestUiDisplay = AutoUi.create_displayfile(config_autoui=config_ui)
    def test_ui_prev(fpth):
        display(TestUiDisplay(fpth))
    
    test_ui = DisplayFile(path=tests_constants.PATH_TEST_AUI, user_file_renderers={'.aui.json':test_ui_prev})

    display(test_ui)


