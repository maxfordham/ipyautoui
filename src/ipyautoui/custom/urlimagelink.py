
# +


from IPython.display import display, HTML, clear_output
import ipywidgets as w
import traitlets as tr


# +
class UrlImageLink(w.HBox):
    """a simple widget (inherits an HBox) for creating a clickable
    url link from an image"""

    url = tr.Unicode()
    path_image = tr.Unicode()
    width = tr.Integer(default_value=200)
    height = tr.Integer(default_value=200)
    tooltip = tr.Unicode(default_value="")
    font_size = tr.Integer(default_value=20)
    description = tr.Unicode(allow_none=True)
    whitespace = tr.Integer(default_value=20)

    @tr.observe(
        "url", "path_image", "width", "height", "tooltip", "font_size", "description"
    )
    def update_display(self, change):
        if self.url == "":
            self.layout.display = "none"
        else:
            self.layout.display = "flex"
            self.out.layout.width = f"{self.width + self.font_size*len(self.description)*0.45}px"  # HOTFIX: ipywidget Output needs explicit width to work in voila. Remove once resolved
            with self.out:
                clear_output()
                display(self.html)

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.out = w.Output()
        super().__init__(*args, **kwargs)
        self.children = [self.out]

    @property
    def html(self):
        self.html_image = f"""<img border="0" src="{self.path_image}"width={self.width} height={self.height}>"""
        if self.description is not None:
            html = f"""<!DOCTYPE html>
                    <html>
                    <style>
                      .aligned {{
                      display: flex;
                      align-items: center;
                    }}
                    .text {{
                      font-size: {self.font_size}px;
                      padding-left: {self.whitespace}px;
                    }}
                    </style>
                    <body>
                        <a href="{self.url}" title="{self.tooltip}" target="_blank">
                            <div class="aligned">
                                <div>
                                    {self.html_image}
                                </div>
                                <span class=text>{self.description}</span>
                            </div>
                        </a>
                    </body>
                    </html>
                    """
        else:
            html = self.html_image
        return HTML(html)


if __name__ == "__main__":
    im = UrlImageLink(
        url="https://github.com/maxfordham/ipyautoui",
        path_image="https://github.com/maxfordham/ipyautoui/blob/main/docs/images/logo.png?raw=true",
        description="<b>ipyautoui</b>",
        width=150,
        font_size=30,
        whitespace=40,
    )
    display(im)
