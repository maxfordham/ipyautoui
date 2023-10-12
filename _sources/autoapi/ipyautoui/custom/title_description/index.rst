:py:mod:`ipyautoui.custom.title_description`
============================================

.. py:module:: ipyautoui.custom.title_description

.. autoapi-nested-parse::

   generic support for observed title and description



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.title_description.TitleDescription
   ipyautoui.custom.title_description.Test




.. py:class:: TitleDescription(**kwargs)

   Bases: :py:obj:`traitlets.HasTraits`

   The base class for all classes that have descriptors.

   .. py:attribute:: title

      

   .. py:attribute:: description

      

   .. py:attribute:: show_title

      

   .. py:method:: observe_title(on_change)


   .. py:method:: observe_description(on_change)


   .. py:method:: observe_show_title(on_change)


   .. py:method:: _update_title_description()



.. py:class:: Test(**kwargs)

   Bases: :py:obj:`ipywidgets.HBox`, :py:obj:`TitleDescription`

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


