:py:mod:`ipyautoui.demo_schemas.nested`
=======================================

.. py:module:: ipyautoui.demo_schemas.nested


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.nested.NestedObject
   ipyautoui.demo_schemas.nested.RecursiveNest
   ipyautoui.demo_schemas.nested.Nested




.. py:class:: NestedObject(**data: Any)

   Bases: :py:obj:`ipyautoui.basemodel.BaseModel`

   description in docstring

   .. py:attribute:: string1
      :type: str

      

   .. py:attribute:: int_slider1
      :type: typing_extensions.Annotated[int, Field(ge=0, le=3)]
      :value: 2

      

   .. py:attribute:: int_text1
      :type: int
      :value: 1

      


.. py:class:: RecursiveNest(**data: Any)

   Bases: :py:obj:`ipyautoui.basemodel.BaseModel`

   description in RecursiveNest docstring

   .. py:attribute:: string1
      :type: str

      

   .. py:attribute:: int_slider1
      :type: typing_extensions.Annotated[int, Field(ge=1, le=3)]
      :value: 2

      

   .. py:attribute:: int_text1
      :type: int
      :value: 1

      

   .. py:attribute:: nested
      :type: NestedObject

      


.. py:class:: Nested(**data: Any)

   Bases: :py:obj:`ipyautoui.basemodel.BaseModel`

   demonstrates nested objects

   .. py:attribute:: nested
      :type: NestedObject

      

   .. py:attribute:: recursive_nest
      :type: RecursiveNest

      

   .. py:attribute:: array_simple
      :type: list[str]

      

   .. py:attribute:: array_objects
      :type: list[NestedObject]

      

   .. py:attribute:: nullable_list
      :type: list[str]

      

   .. py:attribute:: nullable_object
      :type: NestedObject

      


