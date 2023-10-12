:py:mod:`ipyautoui.custom.showhide`
===================================

.. py:module:: ipyautoui.custom.showhide


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.showhide.ShowHide




Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.showhide.d


.. py:class:: ShowHide(fn_display: Callable = lambda: w.HTML('😲'), title: str = 'title', auto_open: bool = False, button_width: str = None)

   Bases: :py:obj:`ipywidgets.VBox`

   simple show/hide widget that displays output of a callable that is pass as the input

   .. py:attribute:: fn_display

      

   .. py:attribute:: is_show

      

   .. py:attribute:: title

      

   .. py:method:: _fn_display()


   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: check_is_show(on_change)


   .. py:method:: show()


   .. py:method:: hide()


   .. py:method:: _observe_title(change)


   .. py:method:: _observe_fn_display(change)


   .. py:method:: display_out(click)



.. py:data:: d

   

