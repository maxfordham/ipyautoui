:py:mod:`ipyautoui.demo_schemas.nullable_core_ipywidgets`
=========================================================

.. py:module:: ipyautoui.demo_schemas.nullable_core_ipywidgets


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.nullable_core_ipywidgets.FruitEnum
   ipyautoui.demo_schemas.nullable_core_ipywidgets.NullableCoreIpywidgets




.. py:class:: FruitEnum

   Bases: :py:obj:`str`, :py:obj:`enum.Enum`

   fruit example.

   .. py:attribute:: apple
      :value: 'apple'

      

   .. py:attribute:: pear
      :value: 'pear'

      

   .. py:attribute:: banana
      :value: 'banana'

      

   .. py:attribute:: orange
      :value: 'orange'

      


.. py:class:: NullableCoreIpywidgets(**data: Any)

   Bases: :py:obj:`ipyautoui.basemodel.BaseModel`

   This is a test UI form to demonstrate how pydantic class can be used to generate an ipywidget input form.
   Only simple datatypes used (i.e. not lists/arrays or objects).
   All set to be nullable.

   .. py:attribute:: int_slider_req
      :type: typing_extensions.Annotated[int, Field(ge=1, le=3)]

      

   .. py:attribute:: int_slider_nullable
      :type: typing_extensions.Annotated[int, Field(ge=1, le=3)]

      

   .. py:attribute:: int_slider
      :type: typing_extensions.Annotated[int, Field(ge=1, le=3)]

      

   .. py:attribute:: int_text
      :type: int

      

   .. py:attribute:: int_range_slider
      :type: tuple[int, int]

      

   .. py:attribute:: float_slider
      :type: float

      

   .. py:attribute:: float_text
      :type: float

      

   .. py:attribute:: float_text_locked
      :type: float

      

   .. py:attribute:: float_range_slider
      :type: tuple[float, float]

      

   .. py:attribute:: checkbox
      :type: bool

      

   .. py:attribute:: dropdown
      :type: FruitEnum

      

   .. py:attribute:: dropdown_edge_case
      :type: FruitEnum

      

   .. py:attribute:: dropdown_simple
      :type: str

      

   .. py:attribute:: text
      :type: str

      

   .. py:attribute:: text_short
      :type: typing_extensions.Annotated[str, StringConstraints(min_length=0, max_length=20)]

      

   .. py:attribute:: text_area
      :type: typing_extensions.Annotated[str, StringConstraints(min_length=0, max_length=800)]

      


