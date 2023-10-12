:py:mod:`ipyautoui.autoanyof`
=============================

.. py:module:: ipyautoui.autoanyof


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.autoanyof.AnyOf
   ipyautoui.autoanyof.MyEnum
   ipyautoui.autoanyof.MyEnum



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.autoanyof.value_type_as_json
   ipyautoui.autoanyof.get_anyOf_type



.. py:function:: value_type_as_json(value)


.. py:function:: get_anyOf_type(l)


.. py:class:: AnyOf(**kwargs)

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

   .. py:property:: value


   .. py:property:: map_type_title


   .. py:attribute:: allOf

      

   .. py:attribute:: anyOf

      

   .. py:attribute:: selected_item

      

   .. py:attribute:: map_title_type

      

   .. py:attribute:: titles

      

   .. py:attribute:: _value

      

   .. py:method:: _allOf(on_change)


   .. py:method:: _anyOf(on_change)


   .. py:method:: _selected_item(on_change)


   .. py:method:: _init_controls()


   .. py:method:: _init_watch_widget()


   .. py:method:: _watch_widget(on_change)


   .. py:method:: _select(on_change)



.. py:class:: MyEnum

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

   .. py:attribute:: state1
      :value: 'state1'

      

   .. py:attribute:: state2
      :value: 'state2'

      


.. py:class:: MyEnum

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

   .. py:attribute:: state1
      :value: 'state1'

      

   .. py:attribute:: state2
      :value: 'state2'

      


