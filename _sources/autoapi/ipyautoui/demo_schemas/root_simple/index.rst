:py:mod:`ipyautoui.demo_schemas.root_simple`
============================================

.. py:module:: ipyautoui.demo_schemas.root_simple


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.root_simple.RootSimple




.. py:class:: RootSimple(root: RootModelRootType = PydanticUndefined, **data)

   Bases: :py:obj:`pydantic.RootModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/#rootmodel-and-custom-root-types

   A Pydantic `BaseModel` for the root object of the model.

   :ivar root: The root object of the model.
   :ivar __pydantic_root_model__: Whether the model is a RootModel.
   :ivar __pydantic_private__: Private fields in the model.
   :ivar __pydantic_extra__: Extra fields in the model.



   .. py:attribute:: root
      :type: conint(ge=0, le=3)
      :value: 2

      


