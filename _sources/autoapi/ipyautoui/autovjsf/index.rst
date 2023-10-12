:py:mod:`ipyautoui.autovjsf`
============================

.. py:module:: ipyautoui.autovjsf


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.autovjsf.Vjsf
   ipyautoui.autovjsf.AutoVjsf



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.autovjsf.rename_vjsf_schema_keys



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.autovjsf.logger
   ipyautoui.autovjsf.schema
   ipyautoui.autovjsf.autowidget
   ipyautoui.autovjsf.Renderer


.. py:data:: logger

   

.. py:function:: rename_vjsf_schema_keys(obj, old='x_', new='x-')

   recursive function to replace all keys beginning x_ --> x-
   this allows schema Field keys to be definied in pydantic and then
   converted to vjsf compliant schema


.. py:class:: Vjsf(*args, **kwargs)

   Bases: :py:obj:`ipyvuetify.VuetifyTemplate`

   Widget that can be inserted into the DOM

   Parameters
   ----------
   tooltip: str
      tooltip caption
   layout: InstanceDict(Layout)
      widget layout

   .. py:attribute:: template_file

      

   .. py:attribute:: vjsf_loaded

      

   .. py:attribute:: value

      

   .. py:attribute:: schema

      

   .. py:attribute:: valid

      


.. py:data:: schema

   

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



.. py:data:: autowidget

   

.. py:data:: Renderer

   

