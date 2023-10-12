:py:mod:`ipyautoui.mydocstring_display`
=======================================

.. py:module:: ipyautoui.mydocstring_display

.. autoapi-nested-parse::

   wrappers around mydocstring.
   consider incorporating into the core package.

   this is used by the python file previewer allowing the file to be
   rendered either as a markdown file from the module level docstring
   or a python file.



Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.mydocstring_display.read_module_docstring
   ipyautoui.mydocstring_display.list_items_after
   ipyautoui.mydocstring_display.docstring_img_list
   ipyautoui.mydocstring_display.function_docstring
   ipyautoui.mydocstring_display.module_docstring
   ipyautoui.mydocstring_display.docstringimgs_from_path
   ipyautoui.mydocstring_display.display_doc_imgs
   ipyautoui.mydocstring_display.display_module_docstring
   ipyautoui.mydocstring_display.display_function_docstring
   ipyautoui.mydocstring_display.docstrings_to_md
   ipyautoui.mydocstring_display.md_to_file
   ipyautoui.mydocstring_display.fpth_chg_extension
   ipyautoui.mydocstring_display.docstring_to_mdfile



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.mydocstring_display.str_md


.. py:function:: read_module_docstring(fpth)

   :param fpth: filepath of the script
   :type fpth: str

   Returns
       docstring(str): module docstring


.. py:function:: list_items_after(li, after='Image')

   list all items in list after a given item
   is found

   :param li:
   :type li: list
   :param \*\*after: list item after which new list begins
                     uses find in so partial string matches work
   :type \*\*after: ?

   :returns: category
   :rtype: li_ (list)


.. py:function:: docstring_img_list(doc, fpth=None)

   creates list of fpths for images.
   if fpth != None, assumes images are relative to script files


.. py:function:: function_docstring(fpth, function_name)

   outputs markdown string given function name and fpth

   :param fpth: [description]
   :type fpth: [type]
   :param function_name: [description]
   :type function_name: [type]

   :returns: markdown string
   :rtype: d


.. py:function:: module_docstring(fpth)

   module level markdown docstring

   :param fpth: python script fpth
   :type fpth: [type]

   :returns: markdown string
   :rtype: [str]


.. py:function:: docstringimgs_from_path(fpth)


.. py:function:: display_doc_imgs(li)


.. py:function:: display_module_docstring(fpth)


.. py:function:: display_function_docstring(fpth, function_name)


.. py:function:: docstrings_to_md(fpth_py, functions=None)


.. py:function:: md_to_file(str_md, fpth_md)


.. py:function:: fpth_chg_extension(fpth, new_ext='docx')


.. py:function:: docstring_to_mdfile(fpth_py, fpth_md=None, functions=None)


.. py:data:: str_md

   

