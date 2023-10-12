:py:mod:`ipyautoui.custom.iterable`
===================================

.. py:module:: ipyautoui.custom.iterable

.. autoapi-nested-parse::

   A generic iterable object.

   Creates an array object where widgets can be added or removed. if the widgets have a "value" or "_value" trait the
   that trait is automatically watched / observed for changes.

   This item is used for the AutoObject `array`.



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.iterable.ItemControl
   ipyautoui.custom.iterable.ItemBox
   ipyautoui.custom.iterable.Array
   ipyautoui.custom.iterable.AutoArray
   ipyautoui.custom.iterable.AutoArrayForm
   ipyautoui.custom.iterable.MyString



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.iterable.flip
   ipyautoui.custom.iterable.get_di



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.iterable.logger
   ipyautoui.custom.iterable.BOX
   ipyautoui.custom.iterable.TOGGLE_BUTTON_KWARGS
   ipyautoui.custom.iterable.MyArray
   ipyautoui.custom.iterable.schema
   ipyautoui.custom.iterable.di_arr
   ipyautoui.custom.iterable.di_arr


.. py:data:: logger

   

.. py:data:: BOX

   

.. py:data:: TOGGLE_BUTTON_KWARGS

   

.. py:function:: flip(box, align_horizontal=False)


.. py:class:: ItemControl

   Bases: :py:obj:`enum.Enum`

   Generic enumeration.

   Derive from this class to define new enumerations.

   .. py:attribute:: add_remove
      :value: 'add_remove'

      

   .. py:attribute:: append_only
      :value: 'append_only'

      

   .. py:attribute:: remove_only
      :value: 'remove_only'

      

   .. py:attribute:: none

      


.. py:class:: ItemBox(**kwargs)

   Bases: :py:obj:`ipywidgets.Box`

   Displays multiple widgets in a group.

   The widgets are laid out horizontally.

   Parameters
   ----------
   {box_params}

   Examples
   --------
   >>> import ipywidgets as widgets
   >>> title_widget = widgets.HTML('<em>Box Example</em>')
   >>> slider = widgets.IntSlider()
   >>> widgets.Box([title_widget, slider])

   .. py:attribute:: index

      

   .. py:attribute:: key

      

   .. py:attribute:: add_remove_controls

      

   .. py:attribute:: widget

      

   .. py:method:: _default_key()


   .. py:method:: _add_remove_controls(on_change)


   .. py:method:: _widget(on_change)


   .. py:method:: _remove_only()


   .. py:method:: _append_only()


   .. py:method:: _add_remove()


   .. py:method:: _no_user_controls()


   .. py:method:: set_children()



.. py:class:: Array(**kwargs)

   Bases: :py:obj:`ipywidgets.VBox`

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

   .. py:property:: value


   .. py:attribute:: _value

      

   .. py:attribute:: fn_add

      

   .. py:attribute:: fn_remove

      

   .. py:attribute:: sort_on_index

      

   .. py:attribute:: length

      

   .. py:attribute:: add_remove_controls

      

   .. py:attribute:: align_horizontal

      

   .. py:attribute:: min_items

      

   .. py:attribute:: max_items

      

   .. py:attribute:: type

      

   .. py:method:: _type(proposal)


   .. py:method:: _length(on_change)


   .. py:method:: _valid_fn_remove(proposal)


   .. py:method:: _add_remove_controls(on_change)


   .. py:method:: _align_horizontal(on_change)


   .. py:method:: display_bn_add_from_zero(display: bool)


   .. py:method:: _init_controls()


   .. py:method:: get_length(on_change)


   .. py:method:: _get_attribute(key, get)


   .. py:method:: _init_row_controls(key=None)


   .. py:method:: _sort_boxes()


   .. py:method:: _update_value(on_change)


   .. py:method:: _update_boxes()


   .. py:method:: _append_row(onclick)


   .. py:method:: _add_row(onclick, key=None)


   .. py:method:: add_row(key=None, new_key=None, add_kwargs=None, widget=None)

      add row to array after key. if key=None then append to end


   .. py:method:: _remove_rows(onclick, key=None)


   .. py:method:: remove_row(key=None, fn_onremove=None)



.. py:class:: AutoArray(**kwargs)

   Bases: :py:obj:`Array`

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

   .. py:property:: value


   .. py:attribute:: allOf

      

   .. py:attribute:: items

      

   .. py:attribute:: prefix_items

      

   .. py:method:: _allOf(on_change)


   .. py:method:: _items(on_change)


   .. py:method:: from_schema(schema, value=None)
      :classmethod:



.. py:class:: AutoArrayForm(**kwargs)

   Bases: :py:obj:`AutoArray`, :py:obj:`ipyautoui.custom.title_description.TitleDescription`

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


.. py:class:: MyString(root: RootModelRootType = PydanticUndefined, **data)

   Bases: :py:obj:`pydantic.RootModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/#rootmodel-and-custom-root-types

   A Pydantic `BaseModel` for the root object of the model.

   :ivar root: The root object of the model.
   :ivar __pydantic_root_model__: Whether the model is a RootModel.
   :ivar __pydantic_private__: Private fields in the model.
   :ivar __pydantic_extra__: Extra fields in the model.



   .. py:attribute:: root
      :type: str

      


.. py:data:: MyArray

   

.. py:function:: get_di()


.. py:data:: schema

   

.. py:data:: di_arr

   

.. py:data:: di_arr

   

