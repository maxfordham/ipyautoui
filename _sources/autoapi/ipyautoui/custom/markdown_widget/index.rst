:py:mod:`ipyautoui.custom.markdown_widget`
==========================================

.. py:module:: ipyautoui.custom.markdown_widget

.. autoapi-nested-parse::

   simple markdown widget



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.markdown_widget.MarkdownWidget
   ipyautoui.custom.markdown_widget.Test



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.markdown_widget.markdown_buttons



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.markdown_widget.BUTTON_MIN_SIZE
   ipyautoui.custom.markdown_widget.EXAMPLE_MARKDOWN
   ipyautoui.custom.markdown_widget.HEADER
   ipyautoui.custom.markdown_widget.BOLD
   ipyautoui.custom.markdown_widget.ITALIC
   ipyautoui.custom.markdown_widget.LIST
   ipyautoui.custom.markdown_widget.NUMBERED
   ipyautoui.custom.markdown_widget.IMAGE
   ipyautoui.custom.markdown_widget.LINK
   ipyautoui.custom.markdown_widget.MAP_MARKDOWN
   ipyautoui.custom.markdown_widget.ui


.. py:data:: BUTTON_MIN_SIZE

   

.. py:data:: EXAMPLE_MARKDOWN
   :value: Multiline-String

    .. raw:: html

        <details><summary>Show Value</summary>

    .. code-block:: python

        """
        # Markdown Example
        
        **Markdown** is a plain text format for writing _structured documents_, based on formatting conventions from email and usenet.
        
        See details here: [__commonmark__](https://commonmark.org/help/)
        
        ## lists
        
        - **bold**
        - *italic*
        - `inline code`
        - [links](https://www.markdownguide.org/basic-syntax/)
        
        ## numbers
        
        1. item 1
        1. item 1
        1. item 1
          - sub item
        
        """

    .. raw:: html

        </details>

   

.. py:data:: HEADER
   :value: Multiline-String

    .. raw:: html

        <details><summary>Show Value</summary>

    .. code-block:: python

        """
        # H1
        
        ## H2
        
        ### H3
        
        ...
        """

    .. raw:: html

        </details>

   

.. py:data:: BOLD
   :value: Multiline-String

    .. raw:: html

        <details><summary>Show Value</summary>

    .. code-block:: python

        """
        **bold text**
        """

    .. raw:: html

        </details>

   

.. py:data:: ITALIC
   :value: Multiline-String

    .. raw:: html

        <details><summary>Show Value</summary>

    .. code-block:: python

        """
        *italic text*
        """

    .. raw:: html

        </details>

   

.. py:data:: LIST
   :value: Multiline-String

    .. raw:: html

        <details><summary>Show Value</summary>

    .. code-block:: python

        """
        - list item 1
        - list item 2
        - list item 3
        """

    .. raw:: html

        </details>

   

.. py:data:: NUMBERED
   :value: Multiline-String

    .. raw:: html

        <details><summary>Show Value</summary>

    .. code-block:: python

        """
        1. item 1
        1. item 2
        1. item 3
        """

    .. raw:: html

        </details>

   

.. py:data:: IMAGE
   :value: Multiline-String

    .. raw:: html

        <details><summary>Show Value</summary>

    .. code-block:: python

        """
        ![relative path to image from the markdown file](rel/path/to/image.png)
        """

    .. raw:: html

        </details>

   

.. py:data:: LINK
   :value: Multiline-String

    .. raw:: html

        <details><summary>Show Value</summary>

    .. code-block:: python

        """
        [commonmark-help](https://commonmark.org/help/)
        """

    .. raw:: html

        </details>

   

.. py:data:: MAP_MARKDOWN

   

.. py:function:: markdown_buttons()

   generate markdown widget button bar


.. py:class:: MarkdownWidget(value=None)

   Bases: :py:obj:`ipywidgets.VBox`

   a simple markdown widget for editing snippets of markdown text

   .. py:property:: value


   .. py:attribute:: _value

      

   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: _add_markdown_text(on_click, text='text')


   .. py:method:: _bn_help(onchange)


   .. py:method:: _text(onchange)



.. py:data:: ui

   

.. py:class:: Test(**data: Any)

   Bases: :py:obj:`pydantic.BaseModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/

   A base class for creating Pydantic models.

   :ivar __class_vars__: The names of classvars defined on the model.
   :ivar __private_attributes__: Metadata about the private attributes of the model.
   :ivar __signature__: The signature for instantiating the model.

   :ivar __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
   :ivar __pydantic_core_schema__: The pydantic-core schema used to build the SchemaValidator and SchemaSerializer.
   :ivar __pydantic_custom_init__: Whether the model has a custom `__init__` function.
   :ivar __pydantic_decorators__: Metadata containing the decorators defined on the model.
                                  This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
   :ivar __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
                                        __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
   :ivar __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
   :ivar __pydantic_post_init__: The name of the post-init method for the model, if defined.
   :ivar __pydantic_root_model__: Whether the model is a `RootModel`.
   :ivar __pydantic_serializer__: The pydantic-core SchemaSerializer used to dump instances of the model.
   :ivar __pydantic_validator__: The pydantic-core SchemaValidator used to validate instances of the model.

   :ivar __pydantic_extra__: An instance attribute with the values of extra fields from validation when
                             `model_config['extra'] == 'allow'`.
   :ivar __pydantic_fields_set__: An instance attribute with the names of fields explicitly specified during validation.
   :ivar __pydantic_private__: Instance attribute with the values of private attributes set on the model instance.


   .. py:attribute:: num
      :type: int

      

   .. py:attribute:: label
      :type: str

      

   .. py:attribute:: md
      :type: str

      


