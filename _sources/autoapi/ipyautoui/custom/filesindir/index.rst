:py:mod:`ipyautoui.custom.filesindir`
=====================================

.. py:module:: ipyautoui.custom.filesindir


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.filesindir.FilesInDir
   ipyautoui.custom.filesindir.ListStrings
   ipyautoui.custom.filesindir.MatchStrings
   ipyautoui.custom.filesindir.FindFiles




Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.filesindir.PATTERNS_DES
   ipyautoui.custom.filesindir.fdir


.. py:data:: PATTERNS_DES
   :value: Multiline-String

    .. raw:: html

        <details><summary>Show Value</summary>

    .. code-block:: python

        """
        list of glob pattern match strings that will be searched within fdir
        ref: https://facelessuser.github.io/wcmatch/pathlib/
        """

    .. raw:: html

        </details>

   

.. py:class:: FilesInDir(**data: Any)

   Bases: :py:obj:`ipyautoui.basemodel.BaseModel`

   object that uses validation to find fpths in fdir that matches patterns

   .. py:attribute:: fdir
      :type: pathlib.Path

      

   .. py:attribute:: recursive
      :type: bool
      :value: True

      

   .. py:attribute:: patterns
      :type: List[str]

      

   .. py:attribute:: fpths
      :type: List[pathlib.Path]
      :value: []

      

   .. py:method:: _fdir(v, values)

      if no key given return uuid.uuid4()


   .. py:method:: _patterns(v, values)

      if no key given return uuid.uuid4()


   .. py:method:: _fpths(v, values)

      if no key given return uuid.uuid4()



.. py:class:: ListStrings(value)

   Bases: :py:obj:`ipywidgets.VBox`, :py:obj:`traitlets.HasTraits`

   Displays multiple widgets vertically using the flexible box model.

   Parameters
   ----------
   {box_params}

   Examples
   --------
   >>> import ipywidgets as widgets
   >>> title_widget = widgets.HTML('<em>Vertical Box Example</em>')
   >>> slider = widgets.IntSlider()
   >>> widgets.VBox([title_widget, slider])

   .. py:attribute:: value

      

   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: _value(on_change)



.. py:class:: MatchStrings(value, match_strings=None, fn_onmatch=lambda x: x)

   Bases: :py:obj:`ListStrings`

   Displays multiple widgets vertically using the flexible box model.

   Parameters
   ----------
   {box_params}

   Examples
   --------
   >>> import ipywidgets as widgets
   >>> title_widget = widgets.HTML('<em>Vertical Box Example</em>')
   >>> slider = widgets.IntSlider()
   >>> widgets.VBox([title_widget, slider])

   .. py:method:: assign_status(item)


   .. py:method:: _value(on_change)



.. py:class:: FindFiles(fdir: pathlib.Path, title='', patterns: List = [], fpths=None, recursive=False, editable_fdir=False, editable_patterns=False, match_files=None)

   Bases: :py:obj:`ipywidgets.VBox`, :py:obj:`traitlets.HasTraits`

   Displays multiple widgets vertically using the flexible box model.

   Parameters
   ----------
   {box_params}

   Examples
   --------
   >>> import ipywidgets as widgets
   >>> title_widget = widgets.HTML('<em>Vertical Box Example</em>')
   >>> slider = widgets.IntSlider()
   >>> widgets.VBox([title_widget, slider])

   .. py:property:: fdir


   .. py:property:: patterns


   .. py:property:: pydantic_obj


   .. py:property:: editable_fdir


   .. py:property:: editable_patterns


   .. py:attribute:: value

      

   .. py:method:: fn_add_pattern(value=None)


   .. py:method:: _patterns(on_change)


   .. py:method:: _fdir(on_change)


   .. py:method:: _refresh(on_click)


   .. py:method:: _init_form()


   .. py:method:: _init_controls()



.. py:data:: fdir
   :value: '../'

   

