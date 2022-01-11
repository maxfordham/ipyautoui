import pathlib
import json
import importlib
from typing import Type
from markdown import markdown
import ipywidgets as widgets
from IPython.display import display, Markdown
import codecs
from pydantic import BaseModel
import typing

try: 
    from mf_file_utilities import go as open_file
except:
    def open_file(path):
        subprocess.call(['open', path])


def display_pydantic_json(pydantic_obj: typing.Type[BaseModel]):
    parsed = json.loads(pydantic_obj.json())
    s = json.dumps(parsed, indent=2)  # , sort_keys=True)
    return Markdown("\n```Python\n" + s + "\n```")

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
        json_file = json.loads(f.read())
    return json_file

def del_cols(df, cols):
    """delete a pandas column if it is in
    the column index otherwise ignore it. """
    if type(cols) == str:
        try:
            del df[cols]
        except:
            print(cols + ' is not in column index')
    else:
        for col in cols:
            try:
                del df[col]
            except:
                print(col + ' is not in column index')
    return df


def del_matching(df, string):
    """
    deletes columns if col name matches string
    """
    matching = [s for s in list(df) if string in s]
    df = del_cols(df, matching)
    return df

#  from mf_modules.jupyter_formatting import md_fromfile, display_python_file
#  ------------------------------------------------------------------------------------------------
def md_fromfile(fpth):
    """
    read an md file and display in jupyter notebook

    Note:
        the markdown content (e.g. images) needs to be pathed relative to the jupyter notebook 
        that you're displaying from rather than the to the markdown file that you're displaying. 
        this can be confusing! 
        
    Args:
        fpth:

    Returns:
        displays in IPython notebook
    """
    file = open(fpth,mode='r',encoding='utf-8') # Open a file: file
    all_of_it = file.read() # read all lines at once
    file.close() # close the file
    display(Markdown(all_of_it))

def display_python_file(fpth):
    """
    pass the fpth of a python file and get a
    rendered view of the code.
    """
    with open(fpth, 'r') as myfile:
        data = myfile.read()
    return Markdown("\n```Python\n" + data + "\n```")


def read_txt(fpth,encoding='utf-8',delim=None,read_lines=True):
    '''
    read a .txt file
    
    Args:
        fpth(string): filepath
        encoding(string): https://docs.python.org/3/library/codecs.html, examples:
            utf-16, utf-8, ascii
        delim(char): character to string split, examples:
            '\t', ','
        read_lines(bool): readlines or whole string (delim may not work if read_lines==False

    '''
    with codecs.open(fpth, encoding=encoding) as f:
        if read_lines==True:
            content = f.readlines()
        else:
            content = f.read()
    f.close()
    if delim!=None:
        li = []
        for n in range(0, len(content)):
            li.append(content[n].split(delim))
        return li
    else:
        return content
    
def read_yaml(fpth, encoding='utf8'):
    """
    read yaml file.

    Ref:
        https://stackoverflow.com/questions/1773805/how-can-i-parse-a-yaml-file-in-python"""
    with open(fpth, encoding=encoding) as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return data

def file(self:Type[BaseModel], path: pathlib.Path, **json_kwargs):
    """
    this is a method that is added to the pydantic BaseModel within AutoUi using
    "setattr".
    
    Example:
        ```setattr(self.config_autoui.pydantic_model, 'file', file)```
        
    Args:
        self (pydantic.BaseModel): instance
        path (pathlib.Path): to write file to
    """
    if "indent" not in json_kwargs.keys():
        json_kwargs.update({"indent": 4})
    path.write_text(self.json(**json_kwargs), encoding="utf-8")