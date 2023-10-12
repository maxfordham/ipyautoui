:py:mod:`ipyautoui.autodisplay`
===============================

.. py:module:: ipyautoui.autodisplay

.. autoapi-nested-parse::

   displayfile is used to display certain types of files.
   The module lets us preview a file, open a file, and open its directory.

   .. rubric:: Example

   ::#

       from ipyautoui.constants import load_test_constants
       from ipyautoui.displayfile import DisplayFile, Markdown
       import ipywidgets as w

       DIR_FILETYPES = load_test_constants().DIR_FILETYPES

       fpths = list(pathlib.Path(DIR_FILETYPES).glob("*"))

       # single file
       d = DisplayFile(fpths[7])
       display(d)



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.autodisplay.DisplayObjectActions
   ipyautoui.autodisplay.DisplayFromPath
   ipyautoui.autodisplay.DisplayFromRequest
   ipyautoui.autodisplay.DisplayFromCallable
   ipyautoui.autodisplay.DisplayObject
   ipyautoui.autodisplay.DisplayCallable
   ipyautoui.autodisplay.DisplayRequest
   ipyautoui.autodisplay.DisplayPath
   ipyautoui.autodisplay.AutoDisplay



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.autodisplay.merge_default_renderers
   ipyautoui.autodisplay.get_renderers
   ipyautoui.autodisplay.check_exists
   ipyautoui.autodisplay.url_ok
   ipyautoui.autodisplay.check_callable_in_namespace
   ipyautoui.autodisplay.check_callable
   ipyautoui.autodisplay.display_catfact
   ipyautoui.autodisplay.display_catfact



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.autodisplay.d
   ipyautoui.autodisplay.ORDER_DEFAULT
   ipyautoui.autodisplay.ORDER_NOTPATH
   ipyautoui.autodisplay.d
   ipyautoui.autodisplay.path
   ipyautoui.autodisplay.path
   ipyautoui.autodisplay.path
   ipyautoui.autodisplay.ext
   ipyautoui.autodisplay.tests_constants
   ipyautoui.autodisplay.user_file_renderers
   ipyautoui.autodisplay.tests_constants
   ipyautoui.autodisplay.user_file_renderers
   ipyautoui.autodisplay.test_ui
   ipyautoui.autodisplay.test_ui


.. py:function:: merge_default_renderers(renderers: Optional[dict[str, Callable]], default_renderers: ipyautoui._utils.frozenmap[str, Callable] = DEFAULT_FILE_RENDERERS) -> dict[str, Callable]


.. py:function:: get_renderers(renderers: Optional[dict[str, Callable]], extend_default_renderers: bool = True) -> dict[str, Callable]


.. py:class:: DisplayObjectActions(**data: Any)

   Bases: :py:obj:`pydantic.BaseModel`

   base object with callables for creating a display object

   .. py:attribute:: renderers
      :type: dict[str, Callable]

      

   .. py:attribute:: path
      :type: Union[str, pathlib.Path, pydantic.HttpUrl, Callable]

      

   .. py:attribute:: ext
      :type: Optional[str]

      

   .. py:attribute:: name
      :type: Optional[str]

      

   .. py:attribute:: check_exists
      :type: Optional[Callable]

      

   .. py:attribute:: renderer
      :type: Optional[Callable]

      

   .. py:attribute:: check_date_modified
      :type: Optional[Callable]

      

   .. py:attribute:: model_config

      

   .. py:method:: _renderer(v: Callable, info: pydantic.FieldValidationInfo)
      :classmethod:



.. py:function:: check_exists(path)


.. py:class:: DisplayFromPath(**data: Any)

   Bases: :py:obj:`DisplayObjectActions`

   base object with callables for creating a display object

   .. py:attribute:: path_new
      :type: Optional[pathlib.Path]

      

   .. py:attribute:: open_file
      :type: Optional[Callable]

      

   .. py:attribute:: open_folder
      :type: Optional[Callable]

      

   .. py:attribute:: model_config

      

   .. py:method:: _path(v)
      :classmethod:


   .. py:method:: _path_new(v, info: pydantic.FieldValidationInfo)
      :classmethod:


   .. py:method:: _name(v, info: pydantic.FieldValidationInfo)
      :classmethod:


   .. py:method:: _ext(v, info: pydantic.FieldValidationInfo)
      :classmethod:


   .. py:method:: _check_exists(v, info: pydantic.FieldValidationInfo)
      :classmethod:


   .. py:method:: _check_date_modified(v, info: pydantic.FieldValidationInfo)
      :classmethod:


   .. py:method:: _open_file(v, info: pydantic.FieldValidationInfo)
      :classmethod:


   .. py:method:: _open_folder(v, info: pydantic.FieldValidationInfo)
      :classmethod:



.. py:function:: url_ok(url)


.. py:class:: DisplayFromRequest(**data: Any)

   Bases: :py:obj:`DisplayObjectActions`

   base object with callables for creating a display object

   .. py:attribute:: path
      :type: pydantic.HttpUrl

      

   .. py:method:: _check_exists(v, info: pydantic.FieldValidationInfo)
      :classmethod:


   .. py:method:: _name(v, info: pydantic.FieldValidationInfo)
      :classmethod:



.. py:function:: check_callable_in_namespace(fn: Callable)


.. py:function:: check_callable(fn: Callable)


.. py:class:: DisplayFromCallable(**data: Any)

   Bases: :py:obj:`DisplayObjectActions`

   base object with callables for creating a display object

   .. py:attribute:: path
      :type: Callable

      

   .. py:method:: _check_exists(v, info: pydantic.FieldValidationInfo)
      :classmethod:


   .. py:method:: _name(v, info: pydantic.FieldValidationInfo)
      :classmethod:



.. py:data:: d

   

.. py:data:: ORDER_DEFAULT
   :value: ('exists', 'openpreview', 'openfile', 'openfolder', 'name')

   

.. py:data:: ORDER_NOTPATH
   :value: ('exists', 'openpreview', 'name')

   

.. py:class:: DisplayObject(display_actions, **kwargs)

   Bases: :py:obj:`ipywidgets.VBox`

   class for displaying file-like objects.

   :param auto_open: bool, auto opens preview of __init__
   :param order: list, controls how the UI displays:
                 allowed values are: ("exists", "openpreview", "openfile", "openfolder", "name")

   .. py:attribute:: _value

      

   .. py:attribute:: auto_open

      

   .. py:attribute:: order

      

   .. py:attribute:: display_actions

      

   .. py:method:: _validate_order(proposal)


   .. py:method:: _check_order(order)


   .. py:method:: _observe_order(change)


   .. py:method:: _display_actions(change)


   .. py:method:: _update_bx_bar(order)


   .. py:method:: _init_form()


   .. py:method:: _update_form()


   .. py:method:: _init_controls()


   .. py:method:: check_exists()


   .. py:method:: _openpreview(onchange)



.. py:class:: DisplayCallable(value, ext, renderers=None, extend_default_renderers=True, **kwargs)

   Bases: :py:obj:`DisplayObject`

   class for displaying file-like objects.

   :param auto_open: bool, auto opens preview of __init__
   :param order: list, controls how the UI displays:
                 allowed values are: ("exists", "openpreview", "openfile", "openfolder", "name")


.. py:class:: DisplayRequest(value, ext, renderers=None, extend_default_renderers=True, **kwargs)

   Bases: :py:obj:`DisplayObject`

   class for displaying file-like objects.

   :param auto_open: bool, auto opens preview of __init__
   :param order: list, controls how the UI displays:
                 allowed values are: ("exists", "openpreview", "openfile", "openfolder", "name")


.. py:class:: DisplayPath(value, renderers=None, extend_default_renderers=True, **kwargs)

   Bases: :py:obj:`DisplayObject`

   class for displaying file-like objects.

   :param auto_open: bool, auto opens preview of __init__
   :param order: list, controls how the UI displays:
                 allowed values are: ("exists", "openpreview", "openfile", "openfolder", "name")

   .. py:property:: path


   .. py:property:: value


   .. py:attribute:: _value

      

   .. py:method:: _default_order()


   .. py:method:: _update_form_DisplayPath()


   .. py:method:: _update_path_tooltips()


   .. py:method:: _init_controls_DisplayPath()


   .. py:method:: _openfile(sender)


   .. py:method:: _openfolder(sender)



.. py:data:: d

   

.. py:data:: path
   :value: 'https://catfact.ninja/fact'

   

.. py:data:: path
   :value: 'https://catfact.ninja/fact'

   

.. py:data:: path
   :value: 'https://catfact.ninja/fact'

   

.. py:data:: ext
   :value: '.json'

   

.. py:function:: display_catfact(path)


.. py:data:: tests_constants

   

.. py:data:: user_file_renderers

   

.. py:class:: AutoDisplay(display_objects_actions: List[DisplayObjectActions], patterns: Union[str, List, None] = None, title: Union[str, None] = None, display_showhide: bool = True)

   Bases: :py:obj:`traitlets.HasTraits`

   The base class for all classes that have descriptors.

   .. py:property:: title


   .. py:property:: display_showhide


   .. py:property:: paths


   .. py:property:: map_names_paths


   .. py:property:: display_objects_actions


   .. py:property:: patterns


   .. py:property:: auto_open


   .. py:attribute:: order

      

   .. py:method:: _observe_order(change)


   .. py:method:: from_paths(paths: List[pathlib.Path], renderers=None, patterns: Union[str, List] = None, title: Union[str, None] = None, display_showhide: bool = True)
      :classmethod:


   .. py:method:: from_requests(map_requests: Dict[str, pydantic.HttpUrl], renderers: Optional[Dict[str, Callable]] = None, extend_default_renderers: bool = True, patterns: Union[str, List] = None, title: Union[str, None] = None, display_showhide: bool = True)
      :classmethod:


   .. py:method:: from_callables(map_callables: Dict[str, Callable], renderers=None, extend_default_renderers=True, patterns: Union[str, List] = None, title: Union[str, None] = None, display_showhide: bool = True)
      :classmethod:


   .. py:method:: from_any(paths: List[Union[Dict[str, pydantic.HttpUrl], Dict[str, Callable], pathlib.Path]], renderers=None, extend_default_renderers=True, patterns: Union[str, List] = None, title: Union[str, None] = None, display_showhide: bool = True)
      :classmethod:


   .. py:method:: actions_from_any(paths: List[pathlib.Path], renderers=None)
      :staticmethod:


   .. py:method:: actions_from_paths(paths: List[pathlib.Path], renderers=None)
      :staticmethod:


   .. py:method:: actions_from_requests(map_requests: Dict[str, pydantic.HttpUrl], renderers=None)
      :staticmethod:


   .. py:method:: actions_from_callables(map_callables: Dict[str, Callable], renderers=None)
      :staticmethod:


   .. py:method:: add_from_paths(paths, renderers=None)


   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: display_all(onclick=None)


   .. py:method:: collapse_all(onclick=None)


   .. py:method:: display_default(onclick=None)


   .. py:method:: display()


   .. py:method:: _ipython_display_()


   .. py:method:: _activate_waiting()


   .. py:method:: _update_files()



.. py:data:: tests_constants

   

.. py:data:: user_file_renderers

   

.. py:data:: test_ui

   

.. py:data:: test_ui

   

.. py:function:: display_catfact(path)


