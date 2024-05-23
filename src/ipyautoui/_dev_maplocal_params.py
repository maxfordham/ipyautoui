"""this is only used when running the python files as jupyter notebooks
in the dev environment. It is called with a `%run _dev_maplocal_params.py`
magic command so is not run when the module is imported.
"""

from dotenv import dotenv_values
import pathlib
import os

rootdir = pathlib.Path(__file__).parents[2]
config = dotenv_values(str(rootdir / ".env"))
config["MAPLOCAL_SCRIPT_PATH"] = str(rootdir / config["MAPLOCAL_SCRIPT_PATH"])

for k, v in config.items():
    if v is not None:
        os.environ[k] = v
