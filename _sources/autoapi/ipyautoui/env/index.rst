:py:mod:`ipyautoui.env`
=======================

.. py:module:: ipyautoui.env


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.env.Env




.. py:class:: Env(_case_sensitive: bool | None = None, _env_prefix: str | None = None, _env_file: DotenvType | None = ENV_FILE_SENTINEL, _env_file_encoding: str | None = None, _env_nested_delimiter: str | None = None, _secrets_dir: str | Path | None = None, **values: Any)

   Bases: :py:obj:`pydantic_settings.BaseSettings`

   Base class for settings, allowing values to be overridden by environment variables.

   This is useful in production for secrets you do not wish to save in code, it plays nicely with docker(-compose),
   Heroku and any 12 factor app design.

   All the below attributes can be set via `model_config`.

   :param _case_sensitive: Whether environment variables names should be read with case-sensitivity. Defaults to `None`.
   :param _env_prefix: Prefix for all environment variables. Defaults to `None`.
   :param _env_file: The env file(s) to load settings values from. Defaults to `Path('')`, which
                     means that the value from `model_config['env_file']` should be used. You can also pass
                     `None` to indicate that environment variables should not be loaded from an env file.
   :param _env_file_encoding: The env file encoding, e.g. `'latin-1'`. Defaults to `None`.
   :param _env_nested_delimiter: The nested env values delimiter. Defaults to `None`.
   :param _secrets_dir: The secret files directory. Defaults to `None`.

   .. py:attribute:: IPYAUTOUI_ROOTDIR
      :type: Optional[pathlib.Path]

      

   .. py:method:: _IPYAUTOUI_ROOTDIR(v)
      :classmethod:

      Checks for app.db in parent directory and copies from repo if it does not
      exist.



