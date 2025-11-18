

from IPython.display import IFrame, Javascript, clear_output, display
import ipywidgets as w
import traitlets as tr
from ipyautoui.custom.showhide import ShowHide


# +
def window_open_appmode(url):
    display(
        Javascript(
            'window.open("{url}", "_blank", "toolbar=no,menubar=no,scrollbars=yes,resizable=yes,top=500,left=500,width=1200,height=600");'.format(
                url=url
            )
        )
    )


def window_open(url):
    display(Javascript('window.open("{url}");'.format(url=url)))


class ShowOpenUrl(ShowHide):
    url = tr.Unicode(default_value="https://readthedocs.org/")
    description = tr.Unicode(allow_none=True)
    url_launch = tr.Unicode(default_value=None, allow_none=True)
    description_launch = tr.Unicode(allow_none=True)

    @tr.observe("url")
    def _obs_url_launch(self, change):
        if change["new"] is None:
            self.btn_launch.layout.display = "None"
        else:
            self.btn_launch.layout.display = ""
            self.display_out("click")

    @tr.observe("description_launch")
    def _obs_description_launch(self, change):
        self.btn_launch.description = change["new"]

    @tr.observe("description")
    def _obs_description(self, change):
        self.btn_launch_embedded.description = change["new"]

    def __init__(self, auto_open=False, **kwargs):
        self.out_launcher = w.Output()
        self.btn_launch = w.Button(
            icon="link", layout=w.Layout(flex="12 1 0%", width="auto")
        )
        self.btn_launch_embedded = w.Button(
            icon="link", layout=w.Layout(flex="12 1 0%", width="auto")
        )
        kwargs = kwargs | {"title": ""}

        super().__init__()
        {setattr(self, k, v) for k, v in kwargs.items()}
        self.btn_display.layout = w.Layout(flex="0.5 1 0%", width="auto")
        self.hbx_title.children = [
            self.btn_display,
            self.btn_launch_embedded,
            self.btn_launch,
        ]
        self.fn_display = lambda: IFrame(self.url, width="100%", height="800")
        self._update_controls()
        self.children = list(self.children) + [self.out_launcher]
        if self.url_launch is None:
            self.btn_launch.layout.display = "None"
        if auto_open:
            self.btn_display.value = True

    def fn_launch(self, on_click):
        with self.out_launcher:
            clear_output()
            window_open(self.url_launch)
            clear_output()

    def fn_launch_embedded(self, on_click):
        with self.out_launcher:
            clear_output()
            window_open_appmode(self.url)
            clear_output()

    def _update_controls(self):
        self.btn_launch.on_click(self.fn_launch)
        self.btn_launch_embedded.on_click(self.fn_launch_embedded)


# -

if __name__ == "__main__":
    docs = ShowOpenUrl(
        title="",
        url="https://ipywidgets.readthedocs.io/en/latest/index.html",
        # url_launch="https://wiki.maxfordham.com/aectemplater-docs/_build/html/intro.html",
        description_launch="open readthedocs as standalone window",
        description="open standalone docs",
        auto_open=True,
    )
    display(docs)
