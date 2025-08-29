# +
import ipywidgets as w
import traitlets as tr
import json
import logging

logger = logging.getLogger(__name__)

# +
class JsonableDict(w.VBox):
    _value = tr.Dict() # allow_none=True, default_value={}

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, str):
            self.text.value = value
        elif isinstance(value, dict):
            self.text.value = json.dumps(value)
        elif value is None:
            pass
        else:
            raise ValueError(f"value must be a dict or jsonable string, not {value}")
            

    def __init__(self, **kwargs):
        value = kwargs.get("value")
        kwargs = {k:v for k, v in kwargs.items() if k != "value"}
        self.text = w.Textarea(**kwargs)
        self.out = w.Output()
        self.html = w.HTML()
        super().__init__()
        self.children = [self.text, self.html]
        self._init_controls()
        self.value = value

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



# +
if __name__ == "__main__":
    from IPython.display import display
    jd = JsonableDict(value={"b": 12})
    display(jd)
# +
if __name__ == "__main__":
    display(jd.value) 

# +
if __name__ == "__main__":
    jd.value = {"a": [1,2,3]}

# +
