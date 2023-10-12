:py:mod:`ipyautoui`
===================

.. py:module:: ipyautoui

.. autoapi-nested-parse::

   ipyautoui is used to quickly and efficiently create ipywidgets from pydantic schema.

   The module has the capability to take a pydantic schema and create a ipywidget from that schema.
   The main features being that you can produce a widget from many field types and also save the
   data as a JSON easily.

   ipyautoui is designed to be extensible.
   all widgets, as a minimum must satisfy the following criteria:
   - be initiated by the following keyword arguments (in addition to others as required):
       - schema
       - value
   - the schema must be a valid jsonschema and where possible use the terms defined in jsonschema

   Example::

       from ipyautoui import AutoUi, demo
       demo()




Subpackages
-----------
.. toctree::
   :titlesonly:
   :maxdepth: 3

   custom/index.rst
   demo_schemas/index.rst


Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   _dev_sys_path_append/index.rst
   _utils/index.rst
   _utils_debounce/index.rst
   autoanyof/index.rst
   autobox/index.rst
   autodisplay/index.rst
   autodisplay_renderers/index.rst
   autoform/index.rst
   automapschema/index.rst
   autoobject/index.rst
   autoui/index.rst
   autovjsf/index.rst
   basemodel/index.rst
   constants/index.rst
   demo/index.rst
   env/index.rst
   mydocstring_display/index.rst
   nullable/index.rst


Package Contents
----------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.AutoUi
   ipyautoui.AutoDisplay
   ipyautoui.AutoVjsf



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.demo



.. py:class:: AutoUi(schema, **kwargs)

   Bases: :py:obj:`ipywidgets.VBox`, :py:obj:`ipyautoui.autoform.AutoObjectFormLayout`, :py:obj:`AutoUiFileMethods`, :py:obj:`AutoRenderMethods`

   extends AutoObject and AutoUiCommonMethods to create an
   AutoUi user-input form. The data that can be saved to a json
   file `path` and loaded from a json file.

   :ivar # AutoFileMethods:
   :ivar # ------------------------------:
   :ivar path: path to file

   :vartype path: tr.Instance(klass=pathlib.PurePath, ...
   :ivar # AutoObjectFormLayout:
   :ivar # -------------------------:
   :ivar title: form title
   :vartype title: str
   :ivar description: form description
   :vartype description: str
   :ivar show_description: show the description. Defaults to True.
   :vartype show_description: bool, optional
   :ivar show_title: show the title. Defaults to True.
   :vartype show_title: bool, optional
   :ivar show_savebuttonbar: show the savebuttonbar. Defaults to True.
   :vartype show_savebuttonbar: bool, optional
   :ivar show_raw: show the raw json. Defaults to False.
   :vartype show_raw: bool, optional
   :ivar fn_onshowraw: do not edit
   :vartype fn_onshowraw: callable
   :ivar fn_onhideraw: do not edit
   :vartype fn_onhideraw: callable
   :ivar fns_onsave: additional functions to be called on save
   :vartype fns_onsave: callable
   :ivar fns_onrevert: additional functions to be called on revert

   :vartype fns_onrevert: callable
   :ivar # AutoObject:
   :ivar # -------------------------:
   :ivar _value: use `value` to set and get. the value of the form. this is a dict of the form {key: value}
   :vartype _value: dict
   :ivar fdir: fdir to work from. useful for widgets that link to files. Defaults to None.
   :vartype fdir: path, optional
   :ivar align_horizontal: aligns widgets horizontally. Defaults to True.
   :vartype align_horizontal: bool, optional
   :ivar nested_widgets: allows user to indicate widgets that should be show / hide type. Defaults to [].
   :vartype nested_widgets: list, optional
   :ivar auto_open: automatically opens the nested_widget. Defaults to True.
   :vartype auto_open: bool, optional
   :ivar order: allows user to re-specify the order for widget rows to appear by key name in self.di_widgets
   :vartype order: list
   :ivar order_can_hide_rows: allows user to hide rows by removing them from the order list.
   :vartype order_can_hide_rows: bool
   :ivar insert_rows: e.g. {3:w.Button()}. allows user to insert a widget into the rows. its presence
                      is ignored by the widget otherwise.
   :vartype insert_rows: dict
   :ivar disabled: disables all widgets. If widgets are disabled
                   using schema kwargs this is remembered when re-enabled. Defaults to False.


   :vartype disabled: bool, optional

   .. py:property:: value


   .. py:property:: jsonschema_caller


   .. py:property:: json


   .. py:attribute:: schema

      

   .. py:attribute:: model

      

   .. py:attribute:: _value

      

   .. py:method:: _schema(on_change)


   .. py:method:: _init_controls()


   .. py:method:: _init_watch_widget()


   .. py:method:: _watch_change(on_change)


   .. py:method:: get_fdir(path=None, fdir=None)



.. py:class:: AutoDisplay(display_objects_actions: List[DisplayObjectActions], patterns: Union[str, List, None] = None, title: Union[str, None] = None, display_showhide: bool = True)

   Bases: :py:obj:`traitlets.HasTraits`

   The base class for all classes that have descriptors.

   .. py:property:: title


   .. py:property:: display_showhide


   .. py:property:: paths


   .. py:property:: map_names_paths


   .. py:property:: display_objects_actions


   .. py:property:: patterns


   .. py:property:: auto_open


   .. py:attribute:: order

      

   .. py:method:: _observe_order(change)


   .. py:method:: from_paths(paths: List[pathlib.Path], renderers=None, patterns: Union[str, List] = None, title: Union[str, None] = None, display_showhide: bool = True)
      :classmethod:


   .. py:method:: from_requests(map_requests: Dict[str, pydantic.HttpUrl], renderers: Optional[Dict[str, Callable]] = None, extend_default_renderers: bool = True, patterns: Union[str, List] = None, title: Union[str, None] = None, display_showhide: bool = True)
      :classmethod:


   .. py:method:: from_callables(map_callables: Dict[str, Callable], renderers=None, extend_default_renderers=True, patterns: Union[str, List] = None, title: Union[str, None] = None, display_showhide: bool = True)
      :classmethod:


   .. py:method:: from_any(paths: List[Union[Dict[str, pydantic.HttpUrl], Dict[str, Callable], pathlib.Path]], renderers=None, extend_default_renderers=True, patterns: Union[str, List] = None, title: Union[str, None] = None, display_showhide: bool = True)
      :classmethod:


   .. py:method:: actions_from_any(paths: List[pathlib.Path], renderers=None)
      :staticmethod:


   .. py:method:: actions_from_paths(paths: List[pathlib.Path], renderers=None)
      :staticmethod:


   .. py:method:: actions_from_requests(map_requests: Dict[str, pydantic.HttpUrl], renderers=None)
      :staticmethod:


   .. py:method:: actions_from_callables(map_callables: Dict[str, Callable], renderers=None)
      :staticmethod:


   .. py:method:: add_from_paths(paths, renderers=None)


   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: display_all(onclick=None)


   .. py:method:: collapse_all(onclick=None)


   .. py:method:: display_default(onclick=None)


   .. py:method:: display()


   .. py:method:: _ipython_display_()


   .. py:method:: _activate_waiting()


   .. py:method:: _update_files()



.. py:class:: AutoVjsf(schema, **kwargs)

   Bases: :py:obj:`ipywidgets.VBox`, :py:obj:`ipyautoui.autoui.AutoObjectFormLayout`, :py:obj:`ipyautoui.autoui.AutoUiFileMethods`, :py:obj:`ipyautoui.autoui.AutoRenderMethods`

   Displays multiple widgets vertically using the flexible box model.

   Parameters
   ----------
   {box_params}

   Examples
   --------
   >>> import ipywidgets as widgets
   >>> title_widget = widgets.HTML('<em>Vertical Box Example</em>')
   >>> slider = widgets.IntSlider()
   >>> widgets.VBox([title_widget, slider])

   .. py:property:: json


   .. py:property:: value


   .. py:property:: schema


   .. py:attribute:: _value

      create a vuetify form using ipyvuetify using VJSF

   .. py:method:: get_description()


   .. py:method:: get_title()


   .. py:method:: display_showraw()


   .. py:method:: _init_controls()


   .. py:method:: update_value(on_change)



.. py:function:: demo()


