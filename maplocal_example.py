"""
Environment:

  - os = ubuntu
  - wsl for windows
  - running the the ubuntu file system
"""

import subprocess
import pathlib


def runcmd(cmd):
    return subprocess.run(f"powershell.exe {cmd}", shell=True)


def openpath(path):
    if isinstance(path, pathlib.PurePath):
        path = str(path)
    return runcmd(f"explorer.exe '{path}'")
