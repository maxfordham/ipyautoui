# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
# %run _dev_sys_path_append.py
# %run __init__.py
#
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
    tooltip = t.Unicode(default_value="")
    font_size = t.Integer(allow_none=True)
    description = t.Unicode(allow_none=True)

    def __init__(
        self,
        url,
        path_image,
        tooltip=None,
        description=None,
        font_size=None,
        width=40,
        height=40,
    ):
        super().__init__()
        self.out = w.Output()
        # self._description = w.HTML(description)
        self.children = [self.out]
        self.url = url
        self.path_image = path_image
        if tooltip is not None:
            self.tooltip = tooltip
        self.width = width
        self.height = height
        self.description = description
        self.font_size = font_size
        self._init_controls()
        self.update("")

    def _init_controls(self):
        self.observe(
            self.update,
            names=[
                "url",
                "path_image",
                "width",
                "height",
                "tooltip",
                "font_size",
                "description",
            ],
        )

    @property
    def html(self):
        self.html_image = f"""<img border="0" src="{self.path_image}"width={self.width} height={self.height}>"""
        if self.description is not None:
            style = f"<style> p.ex1 {{font-size: {self.font_size}px;}}</style>"
            html = f"""<!DOCTYPE html>
                    <html>
                        {style}
                        <a href="{self.url}" title="{self.tooltip}" target="_blank">
                            <p class="ex1">
                                {self.html_image}
                                <b>{self.description}</b>
                            </p>
                        </a>
                    </html>
                    """
        else:
            html = self.html_image

        return HTML(html)

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
# -


