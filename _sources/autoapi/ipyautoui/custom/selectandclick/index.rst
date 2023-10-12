:py:mod:`ipyautoui.custom.selectandclick`
=========================================

.. py:module:: ipyautoui.custom.selectandclick


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.selectandclick.SelectAndClick
   ipyautoui.custom.selectandclick.Add
   ipyautoui.custom.selectandclick.Remove
   ipyautoui.custom.selectandclick.Load
   ipyautoui.custom.selectandclick.SelectMultipleAndClick
   ipyautoui.custom.selectandclick.AddMultiple
   ipyautoui.custom.selectandclick.RemoveMultiple




Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.selectandclick.LI
   ipyautoui.custom.selectandclick.ui
   ipyautoui.custom.selectandclick.ui


.. py:class:: SelectAndClick(**kwargs)

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

   .. py:attribute:: value

      

   .. py:attribute:: fn_onclick

      

   .. py:attribute:: fn_get_options

      

   .. py:attribute:: fn_loading_msg

      

   .. py:attribute:: fn_succeed_msg

      

   .. py:attribute:: fn_failed_msg

      

   .. py:attribute:: options

      

   .. py:attribute:: title

      

   .. py:attribute:: message

      

   .. py:attribute:: align_horizontal

      

   .. py:attribute:: align_left

      

   .. py:method:: _observe_value(change)


   .. py:method:: _observe_align_horizontal(change)


   .. py:method:: _observe_align_left(change)


   .. py:method:: align()


   .. py:method:: _observe_options(change)


   .. py:method:: _observe_title(change)


   .. py:method:: _observe_message(change)


   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: update_options()


   .. py:method:: _update_message(on_change)


   .. py:method:: fn_update_message()


   .. py:method:: _update_value(on_change)


   .. py:method:: onclick(on_click)


   .. py:method:: onclick_extra()


   .. py:method:: default_align_horizontal()


   .. py:method:: default_align_left()


   .. py:method:: get_selector_widget()
      :staticmethod:



.. py:class:: Add(**kwargs)

   Bases: :py:obj:`SelectAndClick`

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


.. py:class:: Remove(**kwargs)

   Bases: :py:obj:`SelectAndClick`

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


.. py:class:: Load(**kwargs)

   Bases: :py:obj:`SelectAndClick`

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

   .. py:attribute:: loaded

      

   .. py:method:: _init_load_controls()


   .. py:method:: _update_loaded(on_change)


   .. py:method:: fn_update_message()


   .. py:method:: onclick_extra()



.. py:data:: LI

   

.. py:class:: SelectMultipleAndClick(**kwargs)

   Bases: :py:obj:`SelectAndClick`

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

   .. py:attribute:: value

      

   .. py:method:: onclick(on_click)


   .. py:method:: default_align_horizontal()


   .. py:method:: default_align_left()


   .. py:method:: get_selector_widget()
      :staticmethod:



.. py:class:: AddMultiple(**kwargs)

   Bases: :py:obj:`SelectMultipleAndClick`

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


.. py:class:: RemoveMultiple(**kwargs)

   Bases: :py:obj:`SelectMultipleAndClick`

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


.. py:data:: ui

   

.. py:data:: ui

   

