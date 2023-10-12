:py:mod:`ipyautoui.demo_schemas.override_ipywidgets`
====================================================

.. py:module:: ipyautoui.demo_schemas.override_ipywidgets


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.override_ipywidgets.OverrideIpywidgets




.. py:class:: OverrideIpywidgets(**data: Any)

   Bases: :py:obj:`ipyautoui.basemodel.BaseModel`

   sometimes it isn't possible to guess what widget to use based on type information.
   For example, the Combobox has the same inputs as a Dropdown. You can specify to use
   a specify widget using the `autoui` field.

   .. py:attribute:: combobox
      :type: str

      

   .. py:attribute:: toggle
      :type: bool

      


