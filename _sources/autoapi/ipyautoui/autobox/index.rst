:py:mod:`ipyautoui.autobox`
===========================

.. py:module:: ipyautoui.autobox

.. autoapi-nested-parse::

   create a simple row item for a form. contains some simple automated layout features



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.autobox.Nest
   ipyautoui.autobox.AutoBox




Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.autobox.logger
   ipyautoui.autobox.SPACER
   ipyautoui.autobox.f1
   ipyautoui.autobox.f2
   ipyautoui.autobox.f3
   ipyautoui.autobox.f4
   ipyautoui.autobox.f5
   ipyautoui.autobox.f6
   ipyautoui.autobox.f7
   ipyautoui.autobox.f8
   ipyautoui.autobox.map_format
   ipyautoui.autobox.bx


.. py:data:: logger

   

.. py:data:: SPACER

   

.. py:data:: f1

   

.. py:data:: f2

   

.. py:data:: f3

   

.. py:data:: f4

   

.. py:data:: f5

   

.. py:data:: f6

   

.. py:data:: f7

   

.. py:data:: f8

   

.. py:data:: map_format

   

.. py:class:: Nest

   .. py:property:: get_tgl


   .. py:method:: _init_controls_Nest()


   .. py:method:: _tgl(on_change)



.. py:class:: AutoBox(**kwargs)

   Bases: :py:obj:`ipywidgets.VBox`, :py:obj:`Nest`, :py:obj:`ipyautoui.custom.title_description.TitleDescription`

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

   .. py:property:: format_tuple


   .. py:attribute:: nested

      

   .. py:attribute:: align_horizontal

      

   .. py:attribute:: hide

      

   .. py:attribute:: widget

      

   .. py:attribute:: indent

      

   .. py:method:: _nested(on_change)


   .. py:method:: _align_horizontal(on_change)


   .. py:method:: _indent(on_change)


   .. py:method:: _widget(on_change)


   .. py:method:: _hide(on_change)


   .. py:method:: format_box()



.. py:data:: bx

   

