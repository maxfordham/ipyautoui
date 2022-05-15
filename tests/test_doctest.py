from .constants import DIR_DOCS, DIR_PACKAGE
import subprocess
from ipyautoui import AutoUi, AutoDisplay, AutoVjsf, automapschema

path = automapschema.__file__


class TestDocTests:
    def test_automapschema(self):
        complete = subprocess.call(f"python -m doctest -v {path}", shell=True)
        assert complete == 0
