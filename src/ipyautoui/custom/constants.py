# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.6
#   kernelspec:
#     display_name: Python [conda env:mf_base]
#     language: python
#     name: conda-env-mf_base-xpython
# ---

# +
import immutables
from ipydatagrid import TextRenderer, Expr, VegaExpr

frozenmap = immutables.Map

# +
# Default
kwargs_data_grid_default = frozenmap(
    header_renderer = TextRenderer(
        vertical_alignment="top",
        horizontal_alignment="center",
    )
)

KWARGS_DATAGRID_DEFAULT = frozenmap(
    header_renderer = TextRenderer(
        vertical_alignment="top",
        horizontal_alignment="center",
    )
)
# -

if __name__ == "__main__":
    print(kwargs_datagrid_default)


