import datetime
import pandas as pd
import pathlib

di_test_autologic = {
    'IntSlider': {
        'value': 1,
        'kwargs': {'min':0, 'max':3} 
    },
    'IntText': {
        'value': 1,
        'kwargs': {}
    },
    'IntRangeSlider': {
        'value': (1,4),
        'kwargs': {'min':0, 'max':5}
    },
    'FloatSlider': {
        'value': 1.4,
        'kwargs': {'min':0, 'max':5}
    },
    'FloatText': {
        'value': 1.4,
        'kwargs': {}
    },
    'FloatRangeSlider': {
        'value': (1.5,5.5),
        'kwargs': {'min':0, 'max':5}
    },
    'Checkbox': {
        'value': True,
        'kwargs': {}
    },
    'Dropdown': {
        'value': 'string',
        'kwargs': {'options':['True', False, 'string']}
    },
    'SelectionRangeSlider': {
        'value': (2, 3),
        'kwargs': {'options':list(range(0,6))}
    },
    'SelectMultiple': {
        'value': ['True', False],
        'kwargs': {'options':['True', False, 'string']}
    },
    'Text': {
        'value': 'short text',
        'kwargs': {}
    },
    'Textarea': {
        'value': 'long text' * 10,
        'kwargs': {}
    },
    'Combobox': {
        'value': 'string',
        'kwargs': {'options': ['True', 'string', 'string2'], 'ensure_option_in_kwargs': True}
    },
    'DatePicker': {
        'value': datetime.date(2021, 8, 9),
        'kwargs': {}
    },
    'FileChooser': {
        'value': pathlib.Path('/mnt/c/engDev/git_mf/ipyautoui/ipyautoui/_autoui.ipynb'),
        'kwargs': {}
    },
    'FileUpload': { 
        'value': None,
        'kwargs': {},
    },
    'AutoModelRunName': { 
        #'value': None,
        'autoui_type':"<class 'ipyautoui._custom_widgets.AutoModelRunName'>",
        'kwargs': {},
    },
    'DataGrid': {
        'value': pd.DataFrame.from_dict({'test':[0,1],'df':[1,2]}),
        'kwargs': {}
    }
}