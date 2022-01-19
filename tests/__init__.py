import pathlib
import sys

FDIR_ROOT = pathlib.Path(__file__).parents[1]
FDIR_SRC = FDIR_ROOT / "src"
sys.path.append(str(FDIR_SRC)) # append ipyautoui source
