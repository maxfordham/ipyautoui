# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
# %run __init__.py
# %load_ext lab_black

from IPython.display import display, HTML, clear_output
import ipywidgets as w
import traitlets as t


class UrlImageLink(w.HBox):
    """a simple widget (inherits an HBox) for creating a clickable
    url link from an image"""

    url = t.Unicode()
    path_image = t.Unicode()
    width = t.Integer()
    height = t.Integer()

    def __init__(self, url, path_image, description=None, width=40, height=40):
        super().__init__()
        self.out = w.Output()
        self._description = w.HTML(description)
        self.children = [self.out, self._description]
        self.url = url
        self.path_image = path_image
        self.width = width
        self.height = height

        self._init_controls()
        self.update("")

    @property
    def description(self):
        return self._description.value

    @description.setter
    def description(self, value):
        self._description.value = value

    def _init_controls(self):
        self.observe(self.update, names=["url", "path_image", "width", "height"])

    @property
    def html(self):
        return HTML(
            f"""<!DOCTYPE html>
<html>
<a href="{self.url}" target="_blank">
<img border="0" src="{self.path_image}"width={self.width} height={self.height}>
</a>
</html>
"""
        )

    def update(self, onchange):
        if self.url == "":
            self.layout.display = "None"
        else:
            self.layout.display = ""
            with self.out:
                clear_output()
                display(self.html)


if __name__ == "__main__":
    im = UrlImageLink(
        "https://github.com/maxfordham/ipyautoui",
        "https://github.com/maxfordham/ipyautoui/blob/main/docs/logo.png?raw=true",
    )
    display(im)
