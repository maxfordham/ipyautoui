# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import ipywidgets as w
import traitlets as tr
import json
import logging

logger = logging.getLogger(__name__)

# %%
class JsonableDict(w.VBox):
    _value = tr.Dict()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.text.value = value

    def __init__(self, **kwargs):
        self.text = w.Textarea(**kwargs)
        self.out = w.Output()
        self.html = w.HTML()
        super().__init__()
        self.children = [self.text, self.html]
        self._init_controls()

    def _init_controls(self):
        self.text.observe(self._update, "value")

    def _update(self, on_change):
        try: 
            jsonable_dict = json.loads(self.text.value)
            self.text.layout.border = 'solid 2px green'
            self._value = jsonable_dict
            self.html.value = f"<code>{self.value}</code>"
        except Exception as e:
            self.text.layout.border = 'solid 2px red'
            self.html.value = "<code>not valid json</code>"
            logger.info(e)



# %%
if __name__ == "__main__":
    from IPython.display import display
    jd = JsonableDict()
    display(jd)
# %%
