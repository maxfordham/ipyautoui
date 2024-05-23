"""
wrappers around mydocstring. 
consider incorporating into the core package. 

this is used by the python file previewer allowing the file to be 
rendered either as a markdown file from the module level docstring
or a python file. 
"""

import os
import subprocess
from IPython.display import display, Markdown
import ast

try:
    from IPython.display import (
        Image,
    )  #  this is due to a known issue with xeus-python. remove try except in future.
except:
    pass


def read_module_docstring(fpth):
    """
    Args:
        fpth(str): filepath of the script
    Returns
        docstring(str): module docstring
    """
    with open(fpth, "r") as f:
        tree = ast.parse(f.read())
    try:
        docstring = ast.get_docstring(tree)
    except:
        docstring = "no docstring present"
    return docstring


#  from mf_modules.pydtype_operations import list_items_after
def list_items_after(li, after="Image"):
    """
    list all items in list after a given item
    is found

    Args:
        li (list):
        **after (?): list item after which new list begins
            uses find in so partial string matches work

    Returns:
        li_ (list): category
    """
    li_ = []
    b = False
    for l in li:
        if after in l:
            b = True
        li_.append(b)
    if True not in li_:
        return None
    else:
        index = [n for n in range(0, len(li_)) if li_[n]]
        return li[index[0] : index[len(index) - 1] + 1]


def docstring_img_list(doc, fpth=None):
    """creates list of fpths for images.
    if fpth != None, assumes images are relative to script files"""

    def get_imgs(li):
        li1 = []
        for n in range(1, len(li)):
            if li[n][0:4] != "    ":
                break
            else:
                li1.append(li[n].strip())
        li1 = list(filter(None, li1))
        return li1

    try:
        li = list_items_after(doc.split("\n"), after="Image")
    except:
        li = None
    if li == None:
        return li
    li = get_imgs(li)
    li = [l.split("/") for l in li]  #  so can work on windows and linux
    if fpth is not None:
        li = [os.path.join(os.path.dirname(fpth), *l) for l in li]
    else:
        li = [os.path.join(*l) for l in li]
    return li


def function_docstring(fpth, function_name):
    """outputs markdown string given function name and fpth

    Args:
        fpth ([type]): [description]
        function_name ([type]): [description]

    Returns:
        d: markdown string
    """
    d = subprocess.check_output(["mydocstring", fpth, function_name, "--markdown"])
    li = docstring_img_list(d.decode("utf-8"), fpth=fpth)
    if li != None:
        display_doc_imgs(li)
    d = d.decode("utf-8")
    return d


def module_docstring(fpth):
    """module level markdown docstring

    Args:
        fpth ([type]): python script fpth

    Returns:
        [str]: markdown string
    """
    doc = read_module_docstring(fpth)
    li = docstring_img_list(doc, fpth=fpth)
    if li != None:
        display_doc_imgs(li)
    fpth = os.path.realpath(fpth)
    try:
        d = subprocess.check_output(["mydocstring", fpth, ".", "--markdown"])
        d = d.decode("utf-8")
    except:
        d = ""

    return d


def docstringimgs_from_path(fpth):
    doc = read_module_docstring(fpth)
    li = docstring_img_list(doc, fpth=fpth)
    display_doc_imgs(li)


def display_doc_imgs(li):
    [display(Image(l)) for l in li]


def display_module_docstring(fpth):
    d = module_docstring(fpth)
    display(Markdown(d))


def display_function_docstring(fpth, function_name):
    d = function_docstring(fpth, function_name)
    display(Markdown(d))


def docstrings_to_md(fpth_py, functions=None):
    str_md_mod = module_docstring(fpth_py)
    if functions is not None:
        str_md_fn = "\n## Functions\n"
        for f in functions:
            tmp = function_docstring(fpth_py, f)
            str_md_fn = str_md_fn + tmp
    else:
        str_md_fn = ""
    str_md = str_md_mod + str_md_fn
    return str_md


def md_to_file(str_md, fpth_md):
    with open(fpth_md, "w") as f:
        f.write(str_md)
    return fpth_md


def fpth_chg_extension(fpth, new_ext="docx"):
    return os.path.splitext(fpth)[0] + "." + new_ext


def docstring_to_mdfile(fpth_py, fpth_md=None, functions=None):
    if fpth_md is None:
        fpth_md = fpth_chg_extension(fpth_py, new_ext=".md")
    str_md = docstrings_to_md(fpth_py, functions=None)
    md_to_file(str_md, fpth_md)
    return fpth_md


if __name__ == "__main__":
    # TODO: update / remove and add tests
    if __debug__:
        str_md = module_docstring(__file__)
        print(str_md)
        print("done")
    else:
        import sys

        fpth = sys.argv[1]
        display_module_docstring(fpth)
