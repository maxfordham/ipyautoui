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

# %run ../_dev_sys_path_append.py
# %run __init__.py
# %load_ext lab_black

from IPython.display import IFrame, Javascript, clear_output
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
    url_embed = tr.Unicode(default_value="https://readthedocs.org/")
    url_launch = tr.Unicode(default_value="https://readthedocs.org/")
    des_launch = tr.Unicode(allow_none=True)
    des_embed = tr.Unicode(allow_none=True)

    @tr.observe("url_embed")
    def _obs_url_embed(self, change):
        if self.url_launch == change["old"]:
            self.url_launch = change["new"]
        return change["new"]

    @tr.observe("des_launch")
    def _obs_des_launch(self, change):
        self.btn_launch.description = change["new"]

        return change["new"]

    @tr.observe("des_embed")
    def _obs_des_embed(self, change):
        self.btn_launch_embedded.description = change["new"]
        return change["new"]

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
            self.btn_launch,
            self.btn_launch_embedded,
        ]
        self.fn_display = lambda: IFrame(self.url_embed, width="100%", height="800")
        self._update_controls()
        self.children = list(self.children) + [self.out_launcher]
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
            window_open_appmode(self.url_embed)
            clear_output()

    def _update_controls(self):
        self.btn_launch.on_click(self.fn_launch)
        self.btn_launch_embedded.on_click(self.fn_launch_embedded)


# -

if __name__ == "__main__":
    docs = ShowOpenUrl(
        title="",
        url_embed="https://ipywidgets.readthedocs.io/en/latest/index.html",
        # url_launch="https://wiki.maxfordham.com/aectemplater-docs/_build/html/intro.html",
        des_launch="open docs",
        des_embed="open standalone docs",
        auto_open=True,
    )
    display(docs)


