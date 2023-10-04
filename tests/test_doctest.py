from .constants import DIR_DOCS, DIR_PACKAGE
import subprocess
from ipyautoui import (
    AutoUi,
    AutoDisplay,
    AutoVjsf,
    automapschema,
    autowidgets,
)
import os

# https://docs.pytest.org/en/7.1.x/how-to/doctest.html#how-to-run-doctests
CMD = "pytest --doctest-modules"

# TODO: deprecate - use pytest docs plugin instead


class TestDocTests:
    def test_automapschema(self):
        complete = subprocess.call(f"{CMD} {automapschema.__file__}", shell=True)
        assert complete == 0

    def test_autowidgets(self):
        complete = subprocess.call(f"{CMD} {autowidgets.__file__}", shell=True)
        assert complete == 0
