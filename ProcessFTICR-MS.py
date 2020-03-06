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
# #%%capture

# load all python and interactive tools
from IPython.display import display, HTML, Markdown, Image
#display(Markdown('## STARTING Environment...'))
# %matplotlib widget
# %xmode Plain
# Plain or Minimal.
import spike
from spike.Interactive import INTER as I
import FTICR_INTER as FI



# %%
#display(Markdown('## ... program is Ready'))
#I.hidecode(initial='show', message=False)
w = FI.IFTMS()

# %%
w.datap

# %%
w.MAX_DISP_PEAKS

# %%
w.MAX_DISP_PEAKS

# %%
w.MAX_DISP_PEAKS

# %% [markdown]
# ## TO-DO
#
# - warning message in peak-picking
# - DeltaM in peaklist
# - calibration
# - pp : sigma + %max

# %% [markdown]
# # Documentation

# %% [markdown]
# In the current set-up, the figure can be explored *(zoom, shift, resize, etc)* with the jupyter tools displayed  below the dataset.
# The figure can also be saved as a `png` graphic file.
#
# At anytime, the figure can be frozen by clicking on the blue button on the upper right corner, just rerun the cell for changing it.

# %% [markdown]
# ### Choose the file
# Use `FileChooser()` to choose a file on your disk - The optional `base` argument, starts the exploration on a given location.
#
# Bruker files are named `fid` and are contained in a `*.d` directory.

# %% [markdown]
# ### Peak Detection
# The following is used to perform an interactive peak picking, and output the result
# Use the cursor to choose the sensitivity of the picker.

# %% [markdown]
# ### Calibration
# The calibration used by SPIKE is based on a 2 or 3 parameters equation :
# $$
# f = \frac{A}{m/z} - B + \frac{C}{(m/z)^2}
# $$
# You can change them below:
#

# %% [markdown]
# ---
#
# ### Calibration on reference peaks
# #### *To come soon !*
#

# %% [markdown]
# ### Save processed data
# You can save a dataset, two formats are available:
#
# - Native SPIKE format, `*.msh5` where all informations are stored - run the following cell

# %% [markdown]
# - Or `cvs` format, with only the spectrum (for the peak list, see above) - ( *be carefull this file can be very big*)

# %% [markdown]
# ### superimpose spectra
# you can superimpose several spectra stored as `.msh5` files in order to compare them

# %% [markdown]
# *the following cell display the colormap used here*
