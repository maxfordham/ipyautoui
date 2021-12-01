"""wrapper for ipyfilechooster.FileChooser"""
import pathlib
from traitlets import HasTraits
from traitlets_paths import PurePath  # TODO: create conda recipe for this package
from ipyfilechooser import FileChooser

class FileChooser(FileChooser, HasTraits):
    """inherits ipyfilechooster.FileChooser but initialises
    with a value= kwarg and adds a fc.value property. this 
    follows the same convention as ipywidgets and therefore integrates
    better wiht ipyautoui"""
    value = PurePath()
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
            