import ipywidgets as widgets
from traitlets import HasTraits, Unicode, default, validate, TraitError
import re

class ModelRunName(widgets.HBox, HasTraits):
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