# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %run ../_dev_maplocal_params.py
# %load_ext lab_black

# +

import traceback
import functools
import ipywidgets as w

try:
    from halo import HaloNotebook
except ImportError:
    ImportError("Please install halo: pip install halo")


# TODO: This will most likely move somewhere more generic at some point so update when this happens.
def halo_decorator(
    output_widget: w.Output,
    loading_msg: str = "Loading",
    succeed_msg: str = "Success!",
    failed_msg: str = "Failed",
):
    def halo_(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            output_widget.clear_output()
            with output_widget as out:
                spinner = HaloNotebook(text=loading_msg, spinner="dots")
                try:
                    spinner.start()
                    func(*args, **kwargs)
                    spinner.succeed(succeed_msg)
                    tb = None
                except Exception as e:
                    spinner.fail(failed_msg)
                    print(traceback.format_exc())

        return wrapper

    return halo_
