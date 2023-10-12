:py:mod:`ipyautoui.custom.multiselect_search`
=============================================

.. py:module:: ipyautoui.custom.multiselect_search

.. autoapi-nested-parse::

   multiselect dropdown widget definition. TODO: integrate with ipyautoui

   Reference:
       https://gist.github.com/MattJBritton/9dc26109acb4dfe17820cf72d82f1e6f




Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.multiselect_search.MultiSelectSearch




Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.multiselect_search.BUTTON_WIDTH_MIN
   ipyautoui.custom.multiselect_search.words


.. py:data:: BUTTON_WIDTH_MIN
   :value: '50px'

   

.. py:class:: MultiSelectSearch(options=[], value=[])

   Bases: :py:obj:`ipywidgets.VBox`

   multi-checkbox select widget with search

   Reference:
       multi-select widget:
           https://gist.github.com/MattJBritton/9dc26109acb4dfe17820cf72d82f1e6f

   .. py:property:: options


   .. py:property:: value


   .. py:attribute:: _options

      

   .. py:attribute:: _value

      

   .. py:method:: _init_controls()


   .. py:method:: _check_all(onchange)


   .. py:method:: _uncheck_all(onchange)


   .. py:method:: _delete_checked(onchange)


   .. py:method:: multi_checkbox_widget(options_dict)

      Widget with a search field and lots of checkboxes



.. py:data:: words
   :value: Multiline-String

    .. raw:: html

        <details><summary>Show Value</summary>

    .. code-block:: python

        """
        a
        AAA
        AAAS
        aardvark
        Aarhus
        Aaron
        ABA
        Ababa
        aback
        abacus
        abalone
        abandon
        abase
        abash
        abate
        abbas
        abbe
        abbey
        abbot
        Abbott
        abbreviate
        abc
        abdicate
        abdomen
        abdominal
        abduct
        Abe
        abed
        Abel
            """

    .. raw:: html

        </details>

   

