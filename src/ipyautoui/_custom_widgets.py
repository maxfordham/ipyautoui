"""
widgets that extend the standard ipywidgets with external libraries or compound widgets 
(i.e. creating a new bespoke widget type from existing widgets)
"""
import ipywidgets as widgets
import ipydatagrid as ipg
from ipyfilechooser import FileChooser
import pathlib
import pandas as pd
from traitlets import HasTraits, TraitError, Unicode, default, validate
import re

class AutoUiDataGrid(ipg.DataGrid, HasTraits):
    """wrapper around ipydatagrid. 
    matching the convention for ipywidgets, the "value" parameter 
    is a json string of the ipydatagrid pandas dataframe. using  
    HasTraits from the traitlets library the 
    """
    value = Unicode()
    def __init__(self, value: pd.DataFrame=pd.read_json('{"test":{"0":0,"1":1},"df":{"0":1,"1":2}}'), **kwargs):
        """
        Args:
            value: pd.DataFrame, dataframe to display as Grid. value is updated on change of the 
                ipydatagrid and is observed by the AutoUi widget.
            kwargs: dict, ipydatagrid kwargs that are passed when it is initialized
        """
        if type(value) == str:
            value = pd.read_json(value)
        if 'editable' not in kwargs.keys():
            kwargs = kwargs | {'editable':True}
        if 'layout' not in kwargs.keys():
            kwargs = kwargs | {"height": "300px", "width": "400px"}
            
        super().__init__(value, **kwargs)
        self._set_value('change')
        self._init_controls()
        
    def _init_controls(self):
        self.on_cell_change(self._set_value)
    
    def _set_value(self, onchange):
        self.value = self.data.to_json()
        
class AutoUiFileChooser(FileChooser, HasTraits):
    """inherits ipyfilechooster.FileChooser but initialises
    with a value= kwarg and adds a fc.value property. this 
    follows the same convention as ipywidgets and therefore integrates
    better wiht ipyautoui"""
    value = Unicode()
    def __init__(self, value: pathlib.Path=None, **kwargs):
        try:
            kwargs.pop('title')
        except:
            pass
        if value is None:
            super().__init__(**kwargs)
        else:
            value = pathlib.Path(value)
            if value.is_file():
                if 'filename' in kwargs:
                    del kwargs['filename']
                super().__init__(str(value.parent), filename=value.name, **kwargs)
                self._apply_selection()
            elif value.is_dir():
                super().__init__(str(value), **kwargs)
            else:
                print('path given doesnt exist')
                super().__init__(str(value), **kwargs)
        self._set_value('click')
        self._init_controls()
        
    def _init_controls(self):
        self._select.on_click(self._set_value)
    
    def _set_value(self, onchange):
        if self.selected is not None:
            self.value = self.selected
            

class AutoModelRunName(widgets.HBox, HasTraits):
    """widget for creating an modelling iteration name to a defined format from component parts"""
    value = Unicode()
    
    @validate('value')
    def _valid_value(self, proposal):
        val = proposal['value']
        matched = re.match("[0-9][0-9][0-9][-][a-z,A-Z,0-9]*[-].+", val)
        if not bool(matched):
            raise TraitError('string musts have format: "[0-9][0-9][0-9][-][a-z,A-Z,0-9]*[-].+" , e.g. 000-lean-short_run_description_of_model_run')
        return val
    
    def __init__(self, value='000-lean-short_description_of_model-run', enum=['lean', 'clean', 'green'], disabled_number=False):
        self.value = value
        self.enum = enum
        self.disabled_number = disabled_number
        self._init_form()
        self._init_controls()
        self.update_name('change')
    
    def _set_enum(self):
        if 'enum' in self.kwargs:
            self.enum = self.kwargs['enum']
        else:
            self.enum = ['lean', 'clean', 'green']
            
    def _init_form(self):
        number, runtype_enum, run_description = self.value.split('-', 2)
        self.number = widgets.IntText(value=number,layout={'width':'50px'}, disabled=self.disabled_number)
        self.runtype_enum = widgets.Dropdown(value=runtype_enum, options=self.enum, layout={'width':'100px'})
        self.run_description = widgets.Text(value=run_description)
        self.name = widgets.Text(disabled=True)
        super().__init__(
            children=[self.number, self.runtype_enum, self.run_description, self.name],
        )
        
    def _init_controls(self):
        self.number.observe(self.update_name, 'value')
        self.runtype_enum.observe(self.update_name, 'value')
        self.run_description.observe(self.update_name, 'value')

    def update_name(self, on_change):
        self.name.value = str(self.number.value).zfill(3) \
            + '-' + self.runtype_enum.value \
            + '-' + self.run_description.value.replace(' ','_')
        self.value = self.name.value
            
    
class AutoUiFileUpload(widgets.FileUpload):
    def __init__(self, value: None = None, **kwargs):
        super().__init__(**kwargs)