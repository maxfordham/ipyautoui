"""contains packages global constants"""

import pathlib
from ipydatagrid import TextRenderer
from ipyautoui._utils import frozenmap

# ^ frozenmap
# https://www.python.org/dev/peps/pep-0603/
# https://github.com/MagicStack/immutables

DIR_MODULE = pathlib.Path(__file__).parent
PATH_VJSF_TEMPLATE = DIR_MODULE / "vjsf.vue"
PATH_SVG = DIR_MODULE / "data" / "12-dots-scale-rotate.svg"

BUTTON_WIDTH_MIN = "44px"
BUTTON_WIDTH_MEDIUM = "90px"
BUTTON_HEIGHT_MIN = "25px"
ROW_WIDTH_MEDIUM = "120px"
ROW_WIDTH_MIN = "60px"
BUTTON_MIN_SIZE = frozenmap(width=BUTTON_WIDTH_MIN, height=BUTTON_HEIGHT_MIN)
# ---------------------------

MAGIC_BUTTON_KWARGS = frozenmap(
    {
        "disabled": False,
        "layout": {"width": "44px"},
        "button_style": "warning",
        "icon": "magic",
        "style": {},
        "tooltip": "add many",
    }
)
TRUE_BUTTON_KWARGS = frozenmap(
    icon="check",
    style={"button_color": "lightgreen"},
    # button_style="success",
    tooltip="true",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=True,
)

FILEUPLD_BUTTON_KWARGS = frozenmap(
    icon="upload",
    description="",
    button_style="info",
    layout={"width": "60px"},
    disabled=False,
)
FILEDNLD_BUTTON_KWARGS = frozenmap(
    icon="download",
    description="",
    tooltip="download file",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=False,
)

IMAGE_BUTTON_KWARGS = frozenmap(
    icon="image",
    disabled=False,
    button_style="info",
    layout={"width": "44px"},
    tooltip="images",
)

FALSE_BUTTON_KWARGS = frozenmap(
    icon="times",
    style={"button_color": "tomato"},
    # button_style="success",
    tooltip="false",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=True,
)

DASH_BUTTON_KWARGS = frozenmap(
    icon="circle",
    style={"button_color": "lightyellow"},
    # button_style="success",
    tooltip="",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=True,
)
LOAD_BUTTON_KWARGS = frozenmap(
    icon="upload",
    # style={"button_color":"white"},
    button_style="info",
    layout={"width": BUTTON_WIDTH_MIN},
    disabled=False,
)
PLAY_BUTTON_KWARGS = frozenmap(
    icon="play",
    # style={"button_color":"white"},
    button_style="primary",
    layout={"width": BUTTON_WIDTH_MIN},
    disabled=False,
)
# ---------------------------
ADD_BUTTON_KWARGS = frozenmap(
    icon="plus",
    style={},
    button_style="success",
    tooltip="add item",
    layout={"width": BUTTON_WIDTH_MIN},  # , "height": BUTTON_HEIGHT_MIN
    disabled=False,
)
EDIT_BUTTON_KWARGS = frozenmap(
    icon="edit",
    style={},
    button_style="warning",
    tooltip="edit item",
    layout={"width": BUTTON_WIDTH_MIN},  # , "height": BUTTON_HEIGHT_MIN
    disabled=False,
)
REMOVE_BUTTON_KWARGS = frozenmap(
    icon="minus",
    style={},
    button_style="danger",
    tooltip="remove item",
    layout={"width": BUTTON_WIDTH_MIN},  # , "height": BUTTON_HEIGHT_MIN
    disabled=False,
)
COPY_BUTTON_KWARGS = frozenmap(
    icon="copy",
    style={},
    button_style="primary",
    tooltip="copy item",
    layout={"width": BUTTON_WIDTH_MIN},  # , "height": BUTTON_HEIGHT_MIN
)
RELOAD_BUTTON_KWARGS = frozenmap(
    icon="sync",
    style={},
    button_style="info",
    tooltip="reload",
    layout={"width": BUTTON_WIDTH_MIN},  # , "height": BUTTON_HEIGHT_MIN
    disabled=False,
)
BLANK_BUTTON_KWARGS = frozenmap(
    icon="",
    style={"button_color": "white"},
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=True,
)
HELP_BUTTON_KWARGS = frozenmap(
    icon="question",
    style={},
    # button_style="primary",
    tooltip="help",
    layout={"width": BUTTON_WIDTH_MIN},  # , "height": BUTTON_HEIGHT_MIN
)

DOWNARROW_BUTTON_KWARGS = frozenmap(
    icon="arrow-down",
    layout={"width": "300px"},
    disabled=True,
    style={"button_color": "white"},
)
DELETE_BUTTON_KWARGS = frozenmap(
    icon="trash-alt",
    button_style="danger",
    tooltip="delete",
    layout={"width": BUTTON_WIDTH_MIN},
)

SHOWNULL_ICON_SHOW = "plus"
SHOWNULL_ICON_HIDE = "minus"
KWARGS_SHOWNULL = frozenmap(
    icon=SHOWNULL_ICON_SHOW,
    layout=dict(width=BUTTON_WIDTH_MIN, display=""),
    tooltip="show null form fields",
    style={"font_weight": "bold"},
)
KWARGS_SHOWRAW = frozenmap(
    icon="code",
    layout=dict(width=BUTTON_WIDTH_MIN, display="None"),
    tooltip="show raw data",
    style={"font_weight": "bold"},
)


KWARGS_DATAGRID_DEFAULT = frozenmap(
    header_renderer=TextRenderer(
        vertical_alignment="top",
        horizontal_alignment="center",
    )
)

TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT = "solid yellow 2px"
OPEN_BN_COLOR = "white"
KWARGS_OPENPREVIEW = frozenmap(
    icon="eye",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    tooltip="preview",
    # button_style="warning", #"primary", "success", "info", "warning", "danger"
    style={"font_weight": "bold"},  # ,'button_color':OPEN_BN_COLOR
)
KWARGS_OPENFILE = frozenmap(
    icon="file",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    tooltip="open file with system software",
    style={"font_weight": "bold"},  # , "button_color": OPEN_BN_COLOR},
)
KWARGS_OPENFOLDER = frozenmap(
    icon="folder",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    tooltip="open folder in file-browser",
    style={"font_weight": "bold"},  # , "button_color": OPEN_BN_COLOR},
)

KWARGS_DISPLAY = frozenmap(
    icon="plus",
    tooltip="display all files",
    layout={"width": BUTTON_WIDTH_MIN},  # , "height": BUTTON_HEIGHT_MIN
    disabled=False,
)
KWARGS_DISPLAY_ALL_FILES = frozenmap(
    {**dict(KWARGS_DISPLAY), **{"tooltip": "display all files"}}
)

KWARGS_COLLAPSE = frozenmap(
    icon="minus",
    tooltip="collapse",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=False,
)
KWARGS_COLLAPSE_ALL_FILES = frozenmap(
    {**dict(KWARGS_COLLAPSE), **{"tooltip": "collapse all files"}}
)

KWARGS_HOME_DISPLAY_FILES = frozenmap(
    icon="home",
    tooltip="display default files",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=False,
)


# documentinfo ------------------------------
#  update this with WebApp data. TODO: delete this?
ROLES = (  # TODO: delete from here - now in document_issue
    "Design Lead",
    "Project Engineer",
    "Engineer",
    "Project Coordinator",
    "Project Administrator",
    "Building Performance Modeller",
)

MAP_JSONSCHEMA_TO_IPYWIDGET = frozenmap(
    **{
        "minimum": "min",
        "maximum": "max",
        "enum": "options",
        "examples": "options",
        "default": "value",
    }
)
#  ^ this is how the json-schema names map to ipywidgets.


def load_test_constants():
    """only in use for debugging within the package. not used in production code.

    Returns:
        module: test_constants object
    """
    from importlib.machinery import SourceFileLoader

    path_testing_constants = DIR_MODULE.parents[1] / "tests" / "constants.py"
    test_constants = SourceFileLoader(
        "constants", str(path_testing_constants)
    ).load_module()
    return test_constants
