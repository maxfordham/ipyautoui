# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.6
#   kernelspec:
#     display_name: Python [conda env:ipyautoui]
#     language: python
#     name: conda-env-ipyautoui-xpython
# ---

"""wrapper for ipyfilechooster.FileChooser"""
# %run __init__.py
# %load_ext lab_black

import pathlib
from traitlets import HasTraits, default, validate
from traitlets_paths import PurePath  # TODO: create conda recipe for this package
from ipyfilechooser import FileChooser

class FileChooser(FileChooser, HasTraits):
    """inherits ipyfilechooster.FileChooser but initialises
    with a value= kwarg and adds a fc.value property. this 
    follows the same convention as ipywidgets and therefore integrates
    better wiht ipyautoui
    
    Reference:
        https://github.com/crahan/ipyfilechooser
    """
    _value = PurePath()
    
    @validate('_value')
    def _valid_value(self, proposal):
        if type(proposal['value']) == str:
            proposal['value'] = pathlib.PurePath(proposal['value'])
        return proposal['value']
    
    @default('_value')
    def _default_value(self):
        return pathlib.Path('.')
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value: PurePath):
        """having the setter allows users to pass a new value field to the class which also updates the 
        `selected` argument used by FileChooser"""
        self._value = value
        self.reset(value.parent, value.name)
        self._apply_selection()
    
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
            self._value = self.selected
            
if __name__ == "__main__":
    from ipyautoui.constants import load_test_constants
    test_constants = load_test_constants()
    fc = FileChooser(test_constants.PATH_TEST_AUI.parent)
    display(fc)

if __name__ == "__main__":
    fc.value = test_constants.PATH_TEST_AUI
