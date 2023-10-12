:py:mod:`ipyautoui.custom.multi_toggle_buttons`
===============================================

.. py:module:: ipyautoui.custom.multi_toggle_buttons

.. autoapi-nested-parse::

   # REF: copy and pasted in full from:
   # https://github.com/stas-prokopiev/ipywidgets_toggle_buttons



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.multi_toggle_buttons.BaseToggleButtons
   ipyautoui.custom.multi_toggle_buttons.MultiToggleButtons




Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.multi_toggle_buttons.DICT_LAYOUT_VBOX_ANY
   ipyautoui.custom.multi_toggle_buttons.DICT_LAYOUT_HBOX_ANY
   ipyautoui.custom.multi_toggle_buttons.LOGGER
   ipyautoui.custom.multi_toggle_buttons.wid


.. py:data:: DICT_LAYOUT_VBOX_ANY

   

.. py:data:: DICT_LAYOUT_HBOX_ANY

   

.. py:data:: LOGGER

   

.. py:class:: BaseToggleButtons(widget_parent, **kwargs)

   Bases: :py:obj:`ipywidgets.VBox`

   Abstract class for all toggle buttons

   Values are stored in self.widget_parent when displayed is self.widget
   Which is updated in the moment when display() is launched

   .. py:property:: value

      Getter for value used in widget

   .. py:property:: options

      Getter for options used in widget

   .. py:method:: _update_widget_view()
      :abstractmethod:

      ABSTRACT: Update view of widget according to self.widget_parent


   .. py:method:: _update_buttons_for_new_options()
      :abstractmethod:

      ABSTRACT: Update buttons if options were changed


   .. py:method:: _check_type_of_new_value(new_value)

      Check that the new value has right type


   .. py:method:: _get_button_width(iter_options)
      :staticmethod:

      Get width to use for buttons with given options

      :param iter_options: options for toggle buttons
      :type iter_options: any iterable

      :returns: width in px to use for buttons with given options
      :rtype: int



.. py:class:: MultiToggleButtons(max_chosen_values=999, **kwargs)

   Bases: :py:obj:`BaseToggleButtons`

   Class to show multi toggle buttons with auto width

   .. py:attribute:: _value

      

   .. py:method:: _init_update_value()


   .. py:method:: _update_value(on_change)


   .. py:method:: _update_widget_view()

      Update view of the widget according to all settings


   .. py:method:: _on_click_button_to_choose_option(dict_changes)

      What to do when button to choose options clicked


   .. py:method:: _update_buttons_for_new_options()

      Update buttons if options were changed



.. py:data:: wid

   

