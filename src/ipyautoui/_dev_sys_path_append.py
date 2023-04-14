"""this is only used when running the python files as jupyter notebooks
in the dev environment. It is called with a `%run _dev_sys_path_append.py`
magic command so is not run when the module is imported.
"""
from dotenv import dotenv_values
import pathlib
import os
import sys

rootdir = pathlib.Path(__file__).parents[2]
config = dotenv_values(str(rootdir / ".env"))
config["PYTHONPATH"] = str(rootdir / config["PYTHONPATH"].replace("/",""))
config["MAPLOCAL_SCRIPT_PATH"] = str(rootdir / config["MAPLOCAL_SCRIPT_PATH"])

for k, v in config.items():
    if v is not None:
        os.environ[k] = v

sys.path.append(config["PYTHONPATH"])
# ^ don't know why we have to do this as i think adding to 
#   to PYTHONPATH should deal with this... but alas...