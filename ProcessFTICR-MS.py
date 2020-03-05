# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.2'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # FTICR-MS Processing and Display
#
# a simplified environment for processing 1D Bruker FTICR datasets with `SPIKE`
#
# Run the first python cell by using the ⇥Run button above 
#

# %% [markdown]
# ### Initialization of the environment
# the following cell should be run only once, at the beginning of the processing

# %%
# load all python and interactive tools - run only once
from IPython.display import display, HTML, Markdown, Image
display(Markdown('## STARTING Environment...'))
# %matplotlib widget
# %xmode Plain
# Plain or Minimal.
import spike
from spike.Interactive import INTER as I
I.hidecode(initial='hide', message=False)
import FTICR_INTER as FI
w = FI.IFTMS()
#display(Markdown('## ... program is Ready'))
display(w);


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
# - 

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
