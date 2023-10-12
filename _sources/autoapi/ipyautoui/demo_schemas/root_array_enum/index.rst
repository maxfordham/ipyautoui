:py:mod:`ipyautoui.demo_schemas.root_array_enum`
================================================

.. py:module:: ipyautoui.demo_schemas.root_array_enum


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.root_array_enum.StrEnum
   ipyautoui.demo_schemas.root_array_enum.UniclassProductsUi
   ipyautoui.demo_schemas.root_array_enum.RootArrayEnum




Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.root_array_enum.DI_TEST
   ipyautoui.demo_schemas.root_array_enum.UniclassProducts


.. py:class:: StrEnum

   Bases: :py:obj:`str`, :py:obj:`enum.Enum`

   str(object='') -> str
   str(bytes_or_buffer[, encoding[, errors]]) -> str

   Create a new string object from the given object. If encoding or
   errors is specified, then the object must expose a data buffer
   that will be decoded using the given encoding and error handler.
   Otherwise, returns the result of object.__str__() (if defined)
   or repr(object).
   encoding defaults to sys.getdefaultencoding().
   errors defaults to 'strict'.


.. py:data:: DI_TEST

   

.. py:data:: UniclassProducts

   

.. py:class:: UniclassProductsUi(root: RootModelRootType = PydanticUndefined, **data)

   Bases: :py:obj:`pydantic.RootModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/#rootmodel-and-custom-root-types

   A Pydantic `BaseModel` for the root object of the model.

   :ivar root: The root object of the model.
   :ivar __pydantic_root_model__: Whether the model is a RootModel.
   :ivar __pydantic_private__: Private fields in the model.
   :ivar __pydantic_extra__: Extra fields in the model.



   .. py:attribute:: root
      :type: UniclassProducts

      

   .. py:attribute:: model_config

      


.. py:class:: RootArrayEnum(root: RootModelRootType = PydanticUndefined, **data)

   Bases: :py:obj:`pydantic.RootModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/#rootmodel-and-custom-root-types

   A Pydantic `BaseModel` for the root object of the model.

   :ivar root: The root object of the model.
   :ivar __pydantic_root_model__: Whether the model is a RootModel.
   :ivar __pydantic_private__: Private fields in the model.
   :ivar __pydantic_extra__: Extra fields in the model.



   .. py:attribute:: root
      :type: list[UniclassProductsUi]

      


