:py:mod:`ipyautoui.demo_schemas.root_array`
===========================================

.. py:module:: ipyautoui.demo_schemas.root_array


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.root_array.NestedObject
   ipyautoui.demo_schemas.root_array.RootArray




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

      


.. py:class:: RootArray(root: RootModelRootType = PydanticUndefined, **data)

   Bases: :py:obj:`pydantic.RootModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/#rootmodel-and-custom-root-types

   A Pydantic `BaseModel` for the root object of the model.

   :ivar root: The root object of the model.
   :ivar __pydantic_root_model__: Whether the model is a RootModel.
   :ivar __pydantic_private__: Private fields in the model.
   :ivar __pydantic_extra__: Extra fields in the model.



   .. py:attribute:: root
      :type: list[NestedObject]

      


