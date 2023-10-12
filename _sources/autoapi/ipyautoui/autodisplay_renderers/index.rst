:py:mod:`ipyautoui.autodisplay_renderers`
=========================================

.. py:module:: ipyautoui.autodisplay_renderers

.. autoapi-nested-parse::

   displayfile is used to display certain types of files.
   The module lets us preview a data retrieved from: file, request or callable (< TODO)



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.autodisplay_renderers.PreviewPython
   ipyautoui.autodisplay_renderers.PreviewExcel



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.autodisplay_renderers.getbytes
   ipyautoui.autodisplay_renderers.default_grid
   ipyautoui.autodisplay_renderers.preview_csv
   ipyautoui.autodisplay_renderers.mdboldstr
   ipyautoui.autodisplay_renderers.mdnorms
   ipyautoui.autodisplay_renderers.mdwildcars
   ipyautoui.autodisplay_renderers.mdheader
   ipyautoui.autodisplay_renderers.xlsxtemplated_display
   ipyautoui.autodisplay_renderers.preview_json_string
   ipyautoui.autodisplay_renderers.preview_json
   ipyautoui.autodisplay_renderers.preview_yaml_string
   ipyautoui.autodisplay_renderers.preview_yaml
   ipyautoui.autodisplay_renderers.preview_plotly_json
   ipyautoui.autodisplay_renderers.preview_plotly
   ipyautoui.autodisplay_renderers.Vega
   ipyautoui.autodisplay_renderers.VegaLite
   ipyautoui.autodisplay_renderers.update_vega_data_url
   ipyautoui.autodisplay_renderers.get_vega_data
   ipyautoui.autodisplay_renderers.preview_vega_json
   ipyautoui.autodisplay_renderers.preview_vega
   ipyautoui.autodisplay_renderers.preview_vegalite_json
   ipyautoui.autodisplay_renderers.preview_vegalite
   ipyautoui.autodisplay_renderers.preview_image
   ipyautoui.autodisplay_renderers.preview_svg
   ipyautoui.autodisplay_renderers.preview_video
   ipyautoui.autodisplay_renderers.preview_audio
   ipyautoui.autodisplay_renderers.preview_text_string
   ipyautoui.autodisplay_renderers.preview_text
   ipyautoui.autodisplay_renderers.preview_dir
   ipyautoui.autodisplay_renderers.preview_text_or_dir
   ipyautoui.autodisplay_renderers.preview_markdown
   ipyautoui.autodisplay_renderers.preview_pdf
   ipyautoui.autodisplay_renderers.handle_compound_ext
   ipyautoui.autodisplay_renderers.render_file



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.autodisplay_renderers.ENV
   ipyautoui.autodisplay_renderers.DEFAULT_FILE_RENDERERS


.. py:data:: ENV

   

.. py:function:: getbytes(path: Union[pathlib.Path, pydantic.HttpUrl, Callable]) -> ByteString

   common function for read bytes from: a request, file or callable
   NOTE: if a callable the data must be returned as bytes


.. py:class:: PreviewPython(module, preview_script=True, docstring_priority=True)

   pass the class either a filepath or an imported
   module and get a display output of the modules
   docstring with a toggle option to view the code

   .. py:method:: _handle_input()


   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: _update_title()


   .. py:method:: _show_docstring()


   .. py:method:: _show_me_the_code(sender)


   .. py:method:: display()


   .. py:method:: _ipython_display_()



.. py:function:: default_grid(df, **kwargs)

   thin wrapper for ipy.DataGrid

   Code:
       _kwargs = {
           'layout':{'width':'100%', 'height':'400px'}
       }
       _kwargs.update(kwargs)  # user overides
       g = ipg.DataGrid(df, **_kwargs)
       return g



.. py:function:: preview_csv(path: Union[pathlib.Path, pydantic.HttpUrl, Callable])


.. py:class:: PreviewExcel(path: Union[pathlib.Path, pydantic.HttpUrl, Callable])

   Bases: :py:obj:`ipywidgets.VBox`

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

   .. py:attribute:: path

      

   .. py:attribute:: xl

      

   .. py:method:: _observe_path(change)


   .. py:method:: _observe_xl(change)



.. py:function:: mdboldstr(string, di)

   return bold __key__: value from dict


.. py:function:: mdnorms(di)


.. py:function:: mdwildcars(di)


.. py:function:: mdheader(di)


.. py:function:: xlsxtemplated_display(li)

   displays xlsxtemplated (written using xlsxtemplater) using ipydatagrid


.. py:function:: preview_json_string(json_str)


.. py:function:: preview_json(path: Union[pathlib.Path, pydantic.HttpUrl, Callable])


.. py:function:: preview_yaml_string(yaml_str)


.. py:function:: preview_yaml(path: Union[pathlib.Path, pydantic.HttpUrl, Callable])


.. py:function:: preview_plotly_json(plotly_str)


.. py:function:: preview_plotly(path: Union[pathlib.Path, pydantic.HttpUrl, Callable])


.. py:function:: Vega(spec)

   render Vega in jupyterlab
   https://github.com/jupyterlab/jupyterlab/blob/master/examples/vega/vega-extension.ipynb


.. py:function:: VegaLite(spec)

   render VegaLite in jupyterlab
   https://github.com/jupyterlab/jupyterlab/blob/master/examples/vega/vega-extension.ipynb


.. py:function:: update_vega_data_url(data: dict, path: pathlib.Path) -> dict

   for relative urls, the path is normally given relative to the json file,
   but when viewed in Voila it needs to be relative to the notebook file. This
   updates the relative path

   :param data: vega data
   :type data: dict
   :param path: path of vg.json
   :type path: Path

   :returns: dict with updated data url
   :rtype: dict


.. py:function:: get_vega_data(path: Union[pathlib.Path, pydantic.HttpUrl, Callable])


.. py:function:: preview_vega_json(vega_json)


.. py:function:: preview_vega(path: Union[pathlib.Path, pydantic.HttpUrl, Callable])


.. py:function:: preview_vegalite_json(vegalite_json)


.. py:function:: preview_vegalite(path)


.. py:function:: preview_image(path: Union[pathlib.Path, pydantic.HttpUrl, Callable], *args, **kwargs)


.. py:function:: preview_svg(path: Union[pathlib.Path, pydantic.HttpUrl, Callable], *args, **kwargs)


.. py:function:: preview_video(path: Union[pathlib.Path, pydantic.HttpUrl, Callable], *args, **kwargs)


.. py:function:: preview_audio(path: Union[pathlib.Path, pydantic.HttpUrl, Callable], *args, **kwargs)


.. py:function:: preview_text_string(text_str)


.. py:function:: preview_text(path: Union[pathlib.Path, pydantic.HttpUrl, Callable])


.. py:function:: preview_dir(path: pathlib.Path)

   preview folder


.. py:function:: preview_text_or_dir(path)

   display path with ext == ""


.. py:function:: preview_markdown(path: pathlib.Path)


.. py:function:: preview_pdf(path: pathlib.Path)


.. py:data:: DEFAULT_FILE_RENDERERS

   

.. py:function:: handle_compound_ext(ext, renderers=DEFAULT_FILE_RENDERERS)

   _summary_

   :param ext: _description_
   :type ext: _type_
   :param renderers: _description_. Defaults to DEFAULT_FILE_RENDERERS.
   :type renderers: _type_, optional

   :returns: _description_
   :rtype: _type_


.. py:function:: render_file(path: pathlib.Path, renderers=DEFAULT_FILE_RENDERERS)

   simple renderer.

   .. note::

      this function is not used by AutoDisplay, but is provided here for simple
      API functionality

   :param path:
   :type path: pathlib.Path
   :param renderers: _description_. Defaults to DEFAULT_FILE_RENDERERS.
   :type renderers: _type_, optional

   :returns: something to display


