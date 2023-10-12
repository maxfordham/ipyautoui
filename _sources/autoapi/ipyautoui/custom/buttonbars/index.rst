:py:mod:`ipyautoui.custom.buttonbars`
=====================================

.. py:module:: ipyautoui.custom.buttonbars


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.buttonbars.SaveActions
   ipyautoui.custom.buttonbars.SaveButtonBar
   ipyautoui.custom.buttonbars.StrEnum
   ipyautoui.custom.buttonbars.CrudButtonBar



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.buttonbars.merge_callables
   ipyautoui.custom.buttonbars.add



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.buttonbars.logger
   ipyautoui.custom.buttonbars.actions
   ipyautoui.custom.buttonbars.sb
   ipyautoui.custom.buttonbars.f
   ipyautoui.custom.buttonbars.BUTTONBAR_CONFIG
   ipyautoui.custom.buttonbars.CrudView


.. py:data:: logger

   

.. py:function:: merge_callables(callables: Union[Callable, List[Callable]])


.. py:class:: SaveActions(*args, **kwargs)

   Bases: :py:obj:`traitlets.HasTraits`

   The base class for all classes that have descriptors.

   .. py:attribute:: unsaved_changes

      

   .. py:attribute:: fns_onsave

      

   .. py:attribute:: fns_onrevert

      

   .. py:method:: _default_fns_onsave()


   .. py:method:: _default_fn_revert()


   .. py:method:: fn_save()

      do not edit


   .. py:method:: fn_revert()


   .. py:method:: _add_action(action_name, fn_add, avoid_dupes=True, overwrite_dupes=True, to_beginning=False)


   .. py:method:: fns_onsave_add_action(fn: Callable, avoid_dupes: bool = True, overwrite_dupes: bool = True, to_beginning=False)


   .. py:method:: fns_onrevert_add_action(fn: Callable, avoid_dupes: bool = True, overwrite_dupes: bool = True, to_beginning=False)



.. py:data:: actions

   

.. py:class:: SaveButtonBar(**kwargs)

   Bases: :py:obj:`SaveActions`, :py:obj:`ipywidgets.HBox`

   The base class for all classes that have descriptors.

   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: _save(click)


   .. py:method:: _revert(click)


   .. py:method:: _observe_unsaved_changes(onchange)


   .. py:method:: _observe_tgl_unsaved_changes(onchange)



.. py:data:: sb

   

.. py:data:: f

   

.. py:data:: BUTTONBAR_CONFIG

   

.. py:class:: StrEnum

   Bases: :py:obj:`str`, :py:obj:`enum.Enum`

   str(object='') -> str
   str(bytes_or_buffer[, encoding[, errors]]) -> str

   Create a new string object from the given object. If encoding or
   errors is specified, then the object must expose a data buffer
   that will be decoded using the given encoding and error handler.
   Otherwise, returns the result of object.__str__() (if defined)
   or repr(object).
   encoding defaults to sys.getdefaultencoding().
   errors defaults to 'strict'.


.. py:data:: CrudView

   

.. py:class:: CrudButtonBar(**kwargs)

   Bases: :py:obj:`ipywidgets.HBox`

   Displays multiple widgets horizontally using the flexible box model.

   Parameters
   ----------
   {box_params}

   Examples
   --------
   >>> import ipywidgets as widgets
   >>> title_widget = widgets.HTML('<em>Horizontal Box Example</em>')
   >>> slider = widgets.IntSlider()
   >>> widgets.HBox([title_widget, slider])

   .. py:attribute:: active

      

   .. py:attribute:: fn_add

      

   .. py:attribute:: fn_edit

      

   .. py:attribute:: fn_copy

      

   .. py:attribute:: fn_delete

      

   .. py:attribute:: fn_backward

      

   .. py:attribute:: fn_reload

      

   .. py:method:: _observe_fn_reload(change)


   .. py:method:: _observe_active(change)


   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: _onclick(button_name)


   .. py:method:: _add(onchange)


   .. py:method:: _edit(onchange)


   .. py:method:: _copy(onchange)


   .. py:method:: _delete(onchange)


   .. py:method:: reset_toggles_except(name)


   .. py:method:: _reload(on_click)



.. py:function:: add()


