"""this is only used when running the python files as jupyter notebooks
in the dev environment. It is called with a `%run _dev_sys_path_append.py`
magic command so is not run when the module is imported.
"""
import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parents[1]))
