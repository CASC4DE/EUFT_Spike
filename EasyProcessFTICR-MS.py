# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.3.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # FTICR-MS Processing and Display
#
# a simplified environment for processing 1D Bruker FTICR datasets with `SPIKE`

# %%
# %%capture

# load all python and interactive tools
# %matplotlib widget
# %xmode Plain
# Plain or Minimal.
import spike
import Tools.FTICR_INTER as FI


# %%
#display(Markdown('## ... program is Ready'))
#I.hidecode(initial='show', message=False)
from importlib import reload
reload(FI)
w = FI.IFTMS()

# %% [markdown]
# # display
# Figures can be explored *(zoom, shift, resize, etc)* with the jupyter tools displayed  below the dataset.
#
# The drawing zone can be resized using the little grey triangle on the lower-right corner
#
# Figures can also be saved as a `png` graphic file.

# %% [markdown]
# # Standard processing:
# ### Choose a file
# Only files in the seafile deposit can be handled.
# Use  the selector to choose an experiment. 
#
# ### Load
# The `Load` button will get the transient of the  selected experiment and display it.
# Any previous processing will be lost
#
# ### Process
# Will compute the Spectrum, according to the parameters define in the "Processing Parameters" pane
#
# ### Peak Pick
# Will compute the Peak list, according to the parameters define in the "Processing Parameters" pane
#
# # Panes
# - raw fid: the transient, if loaded
# - spectrum: the processed spectrum, if computed
# - Peak list: the peak list, if computed - can be exported in csv format
# - Processing Parameters: all the parameters used for the processing: 
# - Info: details on the experiment and Processing audit trails

# %% [markdown]
# ### Calibration
# The calibration used by SPIKE is based on a 2 or 3 parameters equation :
# $$
# f = \frac{A}{m/z} - B + \frac{C}{(m/z)^2}
# $$
# where $A$ $B$ and $C$ are imported from the Bruker `ML1` `ML2` `ML3` parameters.
#
# **Be carefull** Bruker uses a sign inversion on `ML2` depending on the value of `ML3` - this is not used, and the equation is allwas the same.
#
# This set-up will be changed in the future for a more flexible and robust set-up

# %% [markdown]
# ## comments
#
# This is a temporary version.
#
# Certain parts are still in dévelopment
# - calibration
# - more efficient peak-picking
# - superimposition of spectra
#

# %%
a_FAIRE = """
to do:
- export to mzml
- peak list
- superimposition
- simple A B C calibration
"""

# %%
