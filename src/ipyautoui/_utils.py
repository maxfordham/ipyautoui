import json
import importlib
from typing import Type
from markdown import markdown
import ipywidgets as widgets

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

def obj_from_string(class_type_string: str) -> Type:
    """
    given the str(type(Obj)) of an Obj, this function
    imports it from the relevant lib (using getattr and
    importlib) and returns the Obj. 
    
    makes it easy to define class used as a string in a json
    object and then use this class to re-initite it.
    
    Args:
        class_type_string
    Returns: 
        obj
        
    Example:
        
    """
    
    def find(s, ch):
        return [i for i, ltr in enumerate(s) if ltr == ch]
    
    cl = class_type_string
    ind = find(cl, "'")
    nm  = cl[ind[0]+1:ind[1]]
    nms =  nm.split('.')
    clss = nms[-1:][0]
    mod = '.'.join(nms[:-1])
    return getattr(importlib.import_module(mod), clss)

def write_json(data, fpth='data.json', sort_keys=True, indent=4):
    '''
    write output to json file
    Args:
        data
        ** sort_keys = True
        ** indent=4
        ** fpth='data.json'
        
    Code:
        out=json.dumps(data, sort_keys=sort_keys, indent=indent)
        f = open(fpth,"w")
        f.write(out)
        f.close()
    '''
    out=json.dumps(data, sort_keys=sort_keys, indent=indent)
    f = open(fpth,"w")
    f.write(out)
    f.close()
    return fpth

def read_json(fpth, encoding='utf8'):
    '''
    read info in a .json file
    '''
    with open(fpth, 'r', encoding=encoding) as f:
        json_file = json.loads(f)
    return json_file