:py:mod:`ipyautoui.custom.showopenurl`
======================================

.. py:module:: ipyautoui.custom.showopenurl


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.showopenurl.ShowOpenUrl



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.showopenurl.window_open_appmode
   ipyautoui.custom.showopenurl.window_open



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.showopenurl.docs


.. py:function:: window_open_appmode(url)


.. py:function:: window_open(url)


.. py:class:: ShowOpenUrl(auto_open=False, **kwargs)

   Bases: :py:obj:`ipyautoui.custom.showhide.ShowHide`

   simple show/hide widget that displays output of a callable that is pass as the input

   .. py:attribute:: url

      

   .. py:attribute:: description

      

   .. py:attribute:: url_launch

      

   .. py:attribute:: description_launch

      

   .. py:method:: _obs_url_launch(change)


   .. py:method:: _obs_description_launch(change)


   .. py:method:: _obs_description(change)


   .. py:method:: fn_launch(on_click)


   .. py:method:: fn_launch_embedded(on_click)


   .. py:method:: _update_controls()



.. py:data:: docs

   

