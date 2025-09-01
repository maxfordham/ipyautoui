
"""simple markdown widget"""


# +
import ipywidgets as w
import functools
import traitlets as tr
from IPython.display import Markdown, clear_output, display
from ipyautoui._utils import frozenmap

# TODO: update the renderer to use pandoc and/or myst, thus getting extended syntax

# +
BUTTON_MIN_SIZE = frozenmap(**{"width": "41px", "height": "25px"})
EXAMPLE_MARKDOWN = """
# Markdown Example

**Markdown** is a plain text format for writing _structured documents_, based on formatting conventions from email and usenet.

See details here: [__commonmark__](https://commonmark.org/help/)

## lists

- **bold**
- *italic*
- `inline code`
- [links](https://www.markdownguide.org/basic-syntax/)

## numbers

1. item 1
1. item 1
1. item 1
  - sub item

"""

HEADER = """
# H1

## H2

### H3

...
"""

BOLD = """
**bold text**
"""

ITALIC = """
*italic text*
"""

LIST = """
- list item 1
- list item 2
- list item 3
"""

NUMBERED = """
1. item 1
1. item 2
1. item 3
"""

IMAGE = """
![relative path to image from the markdown file](rel/path/to/image.png)
"""

LINK = """
[commonmark-help](https://commonmark.org/help/)
"""

MAP_MARKDOWN = frozenmap(
    **{
        "bn_header": HEADER,
        "bn_bold": BOLD,
        "bn_italic": ITALIC,
        "bn_list": LIST,
        "bn_numbered": NUMBERED,
        "bn_image": IMAGE,
        "bn_link": LINK,
    }
)


# -


def markdown_buttons():
    """generate markdown widget button bar"""
    bn_header = w.Button(icon="heading", layout=dict(BUTTON_MIN_SIZE))
    bn_bold = w.Button(icon="bold", layout=dict(BUTTON_MIN_SIZE))
    bn_italic = w.Button(icon="italic", layout=dict(BUTTON_MIN_SIZE))
    bn_list = w.Button(icon="list", layout=dict(BUTTON_MIN_SIZE))
    bn_numbered = w.Button(icon="list-ol", layout=dict(BUTTON_MIN_SIZE))
    bn_image = w.Button(icon="image", layout=dict(BUTTON_MIN_SIZE))
    bn_link = w.Button(icon="link", layout=dict(BUTTON_MIN_SIZE))
    bn_blank = w.Button(
        display=True, style={"button_color": "white"}, layout=dict(BUTTON_MIN_SIZE)
    )
    bn_help = w.ToggleButton(icon="question", layout=dict(BUTTON_MIN_SIZE))
    bx_buttons = w.HBox()
    bx_buttons.children = [
        bn_header,
        bn_bold,
        bn_italic,
        bn_list,
        bn_numbered,
        bn_image,
        bn_link,
        bn_blank,
        bn_help,
    ]
    return (
        bx_buttons,
        bn_header,
        bn_bold,
        bn_italic,
        bn_list,
        bn_numbered,
        bn_image,
        bn_link,
        bn_help,
    )


class MarkdownWidget(w.VBox):
    """a simple markdown widget for editing snippets of markdown text"""

    _value = tr.Unicode(allow_none=True)  # default=""

    def __init__(self, **kwargs):
        self._init_form(**kwargs)
        self._init_controls()
        v = kwargs.get("value")
        if v is None:
            v = ""
        self.value = v

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.text.value = value

    def _init_form(self, **kwargs):
        super().__init__(**{k: v for k, v in kwargs.items() if k != "tooltip"})
        self.text = w.Textarea(layout={"width": "400px", "height": "300px"})
        self.rendered = w.Output()
        self.example_text = w.Textarea(
            value=EXAMPLE_MARKDOWN,
            disabled=True,
            layout={"width": "400px", "height": "300px"},
        )
        self.example_rendered = w.Output()
        self.bx_markdown = w.HBox()
        self.bx_markdown.children = [self.text, self.rendered]
        (
            self.bx_buttons,
            self.bn_header,
            self.bn_bold,
            self.bn_italic,
            self.bn_list,
            self.bn_numbered,
            self.bn_image,
            self.bn_link,
            self.bn_help,
        ) = markdown_buttons()
        self.children = [self.bx_buttons, self.bx_markdown]

    def _init_controls(self):
        self.text.observe(self._text, names="value")
        self.bn_help.observe(self._bn_help, names="value")
        for k, v in MAP_MARKDOWN.items():
            getattr(self, k).on_click(
                functools.partial(self._add_markdown_text, text=v)
            )

    def _add_markdown_text(self, on_click, text="text"):
        self.value = self.value + text

    def _bn_help(self, onchange):
        if self.bn_help.value:
            self.bx_markdown.children = [self.example_text, self.example_rendered]
            with self.example_rendered:
                clear_output()
                display(Markdown(self.example_text.value))
        else:
            self.bx_markdown.children = [self.text, self.rendered]

    def _text(self, onchange):
        self._value = self.text.value
        with self.rendered:
            clear_output()
            display(Markdown(self.text.value))


if __name__ == "__main__":
    ui = MarkdownWidget()
    display(ui)

if __name__ == "__main__":
    from pydantic import BaseModel, Field
    from ipyautoui import AutoUi

    class Test(BaseModel):
        num: int
        label: str
        md: str = Field("adsf", format="markdown")

    display(AutoUi(Test))
