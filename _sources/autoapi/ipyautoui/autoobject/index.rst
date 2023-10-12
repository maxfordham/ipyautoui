:py:mod:`ipyautoui.autoobject`
==============================

.. py:module:: ipyautoui.autoobject

.. autoapi-nested-parse::

   AutoObject - create a



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.autoobject.AutoObject
   ipyautoui.autoobject.AutoObjectForm



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.autoobject._get_value_trait



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.autoobject.logger
   ipyautoui.autoobject.v
   ipyautoui.autoobject.s
   ipyautoui.autoobject.s
   ipyautoui.autoobject.v
   ipyautoui.autoobject.ui
   ipyautoui.autoobject.ui


.. py:data:: logger

   

.. py:function:: _get_value_trait(obj_with_traits)

   gets the trait type for a given object (looks for "_value" and
   "value" allowing use of setters and getters)

   :param obj_with_traits: obj with traits
   :type obj_with_traits: tr.Type

   :raises ValueError: if "_value" or "value" traits don't exist

   :returns: trait type of traitlet
   :rtype: ty.Type


.. py:class:: AutoObject(**kwargs)

   Bases: :py:obj:`ipywidgets.VBox`

   creates an ipywidgets form from a json-schema or pydantic model.
   datatype must be "object"

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

   .. py:property:: default_order


   .. py:property:: value


   .. py:property:: json


   .. py:property:: di_widgets_value


   .. py:attribute:: update_map_widgets

      

   .. py:attribute:: widgets_map

      

   .. py:attribute:: type

      

   .. py:attribute:: allOf

      

   .. py:attribute:: properties

      

   .. py:attribute:: _value

      

   .. py:attribute:: fdir

      

   .. py:attribute:: align_horizontal

      

   .. py:attribute:: nested_widgets

      

   .. py:attribute:: order

      

   .. py:attribute:: order_can_hide_rows

      

   .. py:attribute:: insert_rows

      

   .. py:attribute:: disabled

      

   .. py:attribute:: open_nested

      

   .. py:method:: _default_update_map_widgets()


   .. py:method:: _update_map_widgets(on_change)


   .. py:method:: _widgets_map()


   .. py:method:: _valid_type(proposal)


   .. py:method:: _allOf(on_change)


   .. py:method:: _properties(on_change)


   .. py:method:: _align_horizontal(on_change)


   .. py:method:: _fdir(on_change)


   .. py:method:: validate_insert_rows(proposal)


   .. py:method:: observe_disabled(on_change)


   .. py:method:: _order(proposal)


   .. py:method:: _obs_order(on_change)


   .. py:method:: _order_can_hide_rows(proposal)


   .. py:method:: _default_nested_widgets()


   .. py:method:: _valid_nested_widgets(proposal)


   .. py:method:: observe_open_nested(on_change)


   .. py:method:: _valid_value(proposal)


   .. py:method:: trait_order()
      :classmethod:


   .. py:method:: get_ordered_kwargs(kwargs)


   .. py:method:: from_schema(schema: Union[Type[pydantic.BaseModel], dict], value: dict = None)
      :classmethod:


   .. py:method:: _open_nested()


   .. py:method:: _close_nested()


   .. py:method:: _init_ui()


   .. py:method:: _init_widgets()


   .. py:method:: indent_non_nullable()


   .. py:method:: _insert_rows()


   .. py:method:: _init_controls()


   .. py:method:: set_watcher(key, widget, watch)


   .. py:method:: _init_watch_widgets()


   .. py:method:: _watch_change(change, key=None, watch='value')


   .. py:method:: _update_widgets_from_value()



.. py:class:: AutoObjectForm(**kwargs)

   Bases: :py:obj:`AutoObject`, :py:obj:`ipyautoui.autoform.AutoObjectFormLayout`

   creates an ipywidgets form from a json-schema or pydantic model.
   datatype must be "object"

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

   .. py:method:: display_ui()


   .. py:method:: display_showraw()



.. py:data:: v

   

.. py:data:: s

   

.. py:data:: s

   

.. py:data:: v

   

.. py:data:: ui

   

.. py:data:: ui

   

