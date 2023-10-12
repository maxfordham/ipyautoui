:py:mod:`ipyautoui.custom.widgetcaller_error`
=============================================

.. py:module:: ipyautoui.custom.widgetcaller_error

.. autoapi-nested-parse::

   widget caller error



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.widgetcaller_error.WidgetCallerError




Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.widgetcaller_error.widget


.. py:class:: WidgetCallerError(**kwargs)

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

   .. py:attribute:: widget

      

   .. py:attribute:: error

      

   .. py:attribute:: schema

      

   .. py:attribute:: value

      

   .. py:method:: _observe_widget(change)


   .. py:method:: _observe_error(change)


   .. py:method:: _observe_schema(change)



.. py:data:: widget
   :value: "<class 'ipyautoui.autoobject.AutoObject'>"

   

