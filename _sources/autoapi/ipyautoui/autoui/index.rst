:py:mod:`ipyautoui.autoui`
==========================

.. py:module:: ipyautoui.autoui

.. autoapi-nested-parse::

   autoui is used to automatically create ipywidget user input (UI) form from a pydantic schema.

   This module maps the pydantic fields to appropriate widgets based on type to display the data in the UI.
   It also supports extension, but mapping custom datatypes onto custom widget classes.
   This information can also be stored to file.

   .. rubric:: Example

   see example for a pydantic schema that can be automatically converted into a
   ipywidgets UI. Currently nesting is not supported::

       from ipyautoui.constants import DISPLAY_AUTOUI_SCHEMA_EXAMPLE
       DISPLAY_AUTOUI_SCHEMA_EXAMPLE()



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.autoui.AutoUiFileMethods
   ipyautoui.autoui.AutoRenderMethods
   ipyautoui.autoui.AutoUi



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.autoui.parse_json_file
   ipyautoui.autoui.displayfile_renderer
   ipyautoui.autoui.jsonschema_to_pydantic
   ipyautoui.autoui.get_from_schema_root
   ipyautoui.autoui.summarize_di_callers



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.autoui.logger
   ipyautoui.autoui.fn
   ipyautoui.autoui.fn
   ipyautoui.autoui.fn
   ipyautoui.autoui.fn


.. py:data:: logger

   

.. py:function:: parse_json_file(path: pathlib.Path, model=None)

   read json from file


.. py:function:: displayfile_renderer(path, renderer=None)


.. py:function:: jsonschema_to_pydantic(schema: Type, *, config: Type = None) -> Optional[Type[pydantic.BaseModel]]


.. py:class:: AutoUiFileMethods(*args, **kwargs)

   Bases: :py:obj:`traitlets.HasTraits`

   AutoUiFileMethods is a mixin class that adds file methods to a AutoUi class

   :ivar path: path to file

   :vartype path: tr.Instance(klass=pathlib.PurePath)...

   .. py:attribute:: path

      

   .. py:attribute:: fdir

      

   .. py:method:: _observe_path(proposal)


   .. py:method:: _get_path(path=None) -> pathlib.Path


   .. py:method:: _get_value(v, p)

      :param v: value
      :param p: path

      :returns: dict
      :rtype: value


   .. py:method:: file(path=None)


   .. py:method:: parse_file(path=None) -> dict


   .. py:method:: load_value(value, unsaved_changes=False)


   .. py:method:: load_file(path=None)


   .. py:method:: get_fdir(path=None, fdir=None)



.. py:function:: get_from_schema_root(schema: Dict, key: AnyStr) -> AnyStr


.. py:class:: AutoRenderMethods

   .. py:method:: create_autoui_renderer(schema: Union[Type[pydantic.BaseModel], dict], path=None, **kwargs)
      :classmethod:


   .. py:method:: create_autodisplay_map(schema: Union[Type[pydantic.BaseModel], dict], ext='.json', **kwargs)
      :classmethod:



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



.. py:function:: summarize_di_callers(obj: AutoUi)


.. py:data:: fn

   

.. py:data:: fn

   

.. py:data:: fn

   

.. py:data:: fn

   

