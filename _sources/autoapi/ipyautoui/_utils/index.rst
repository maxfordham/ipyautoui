:py:mod:`ipyautoui._utils`
==========================

.. py:module:: ipyautoui._utils


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui._utils.PyObj



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui._utils.make_new_path
   ipyautoui._utils.getuser
   ipyautoui._utils.str_presenter
   ipyautoui._utils.display_pydantic_json
   ipyautoui._utils._markdown
   ipyautoui._utils.write_json
   ipyautoui._utils.read_json
   ipyautoui._utils.del_cols
   ipyautoui._utils.del_matching
   ipyautoui._utils.display_python_string
   ipyautoui._utils.display_python_file
   ipyautoui._utils.display_python_module
   ipyautoui._utils.read_txt
   ipyautoui._utils.read_yaml
   ipyautoui._utils.file
   ipyautoui._utils.round_sig_figs
   ipyautoui._utils.load_PyObj
   ipyautoui._utils.obj_to_importstr
   ipyautoui._utils.obj_from_importstr
   ipyautoui._utils.argspecs_in_kwargs
   ipyautoui._utils.traits_in_kwargs
   ipyautoui._utils.remove_non_present_kwargs
   ipyautoui._utils.get_ext
   ipyautoui._utils.st_mtime_string
   ipyautoui._utils.check_installed
   ipyautoui._utils.html_link
   ipyautoui._utils.get_user



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui._utils.logger
   ipyautoui._utils.frozenmap


.. py:data:: logger

   

.. py:data:: frozenmap

   

.. py:function:: make_new_path(path, *args, **kwargs)


.. py:function:: getuser()


.. py:function:: str_presenter(dumper, data)

   configures yaml for dumping multiline strings
   Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data


.. py:function:: display_pydantic_json(pydantic_obj: Type[pydantic.BaseModel], as_yaml=False, sort_keys=False)


.. py:function:: _markdown(value='_Markdown_', **kwargs)

   a simple template for markdown text input that templates required input
   fields. additional user defined fields can be added as kwargs


.. py:function:: write_json(data, fpth='data.json', sort_keys=True, indent=4)

   write output to json file
   :param data:
   :param \*\* sort_keys = True:
   :param \*\* indent=4:
   :param \*\* fpth='data.json':

   Code:
       out=json.dumps(data, sort_keys=sort_keys, indent=indent)
       f = open(fpth,"w")
       f.write(out)
       f.close()


.. py:function:: read_json(fpth, encoding='utf8')

   read info in a .json file


.. py:function:: del_cols(df, cols)

   delete a pandas column if it is in
   the column index otherwise ignore it.


.. py:function:: del_matching(df, string)

   deletes columns if col name matches string


.. py:function:: display_python_string(string, show=True, return_str=False, myst_format=False)


.. py:function:: display_python_file(fpth, show=True, return_str=False)

   pass the fpth of a python file and get a
   rendered view of the code.


.. py:function:: display_python_module(mod, show=True, return_str=False)

   pass the fpth of a python file and get a
   rendered view of the code.


.. py:function:: read_txt(fpth, encoding='utf-8', delim=None, read_lines=True)

   read a .txt file

   :param fpth: filepath
   :type fpth: string
   :param encoding: https://docs.python.org/3/library/codecs.html, examples:
                    utf-16, utf-8, ascii
   :type encoding: string
   :param delim: character to string split, examples:
                 '   ', ','
   :type delim: char
   :param read_lines: readlines or whole string (delim may not work if read_lines==False
   :type read_lines: bool


.. py:function:: read_yaml(fpth, encoding='utf8')

   read yaml file.

   Ref:
       https://stackoverflow.com/questions/1773805/how-can-i-parse-a-yaml-file-in-python


.. py:function:: file(self: Type[pydantic.BaseModel], path: pathlib.Path, **json_kwargs)

   this is a method that is added to the pydantic BaseModel within AutoUi using
   "setattr".

   .. rubric:: Example

   ```setattr(self.config_autoui.pydantic_model, 'file', file)```

   :param self: instance
   :type self: pydantic.BaseModel
   :param path: to write file to
   :type path: pathlib.Path


.. py:function:: round_sig_figs(x: float, sig_figs: int)


.. py:class:: PyObj(**data: Any)

   Bases: :py:obj:`pydantic.BaseModel`

   a definition of a python object

   .. py:attribute:: path
      :type: pathlib.Path

      

   .. py:attribute:: obj_name
      :type: str

      

   .. py:attribute:: module_name
      :type: str

      

   .. py:method:: _module_name(v, info: pydantic.FieldValidationInfo)
      :classmethod:



.. py:function:: load_PyObj(obj: PyObj)


.. py:function:: obj_to_importstr(obj: Callable)

   given a callable callable object this will return the
   import string to. From the string the object can be
   initiated again using importlib. This is useful for
   defining a function or class in a json serializable manner

   :param obj: ty.Callable

   :returns: import string
   :rtype: str

   .. rubric:: Example

   >>> obj_from_importstr(pathlib.Path)
   'pathlib.Path'


.. py:function:: obj_from_importstr(importstr: str) -> Type

   given the import string of an object this function and returns the Obj.

   makes it easy to define class used as a string in a json
   object and then use this class to re-initite it.

   :param import_string: == obj.__module__ + '.' + obj.__name__

   :returns: obj

   .. rubric:: Example

   >>> obj_from_importstr('pathlib.Path')
   pathlib.Path


.. py:function:: argspecs_in_kwargs(call: Callable, kwargs: dict)

   get argspecs for kwargs


.. py:function:: traits_in_kwargs(call: Callable, kwargs: dict)

   get traits for kwargs


.. py:function:: remove_non_present_kwargs(callable_: Callable, di: dict)

   do this if required (get allowed args from callable)


.. py:function:: get_ext(fpth)

   get file extension including compound json files


.. py:function:: st_mtime_string(path)

   st_mtime_string for a given path


.. py:function:: check_installed(package_name)


.. py:function:: html_link(url: str, description: str, color: str = 'blue')

   returns an html link string to open in new tab

   :param url:
   :type url: url
   :param description: the text to display for the link
   :type description: str
   :param color: color of description text. Defaults to "blue".
   :type color: str, optional

   :returns: html text
   :rtype: str


.. py:function:: get_user()

   get user. gets JUPYTERHUB_USER if present (i.e. if notebook served via a JupyterHub)


