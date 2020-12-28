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
# # Display utility for 2D FTICR-MS Spectra

# %%
# adapt sys.path to local env
import sys, os
if os.uname().nodename == 'madMacBook':  # a switch for the development environment, add yours if need be
    try:
        done_once
    except:
        print('on my Mac')
        os.chdir('..')
        done_once = True
    else:
        print('already on my Mac')
else:
    local = '.local/lib/python%d.%d/site-packages'%(sys.version_info.major,sys.version_info.minor)
    sys.path = [local] + sys.path

# %%
# %%capture
# load all python and interactive tools
# %matplotlib widget
# %xmode Plain
# Plain or Minimal.
import spike

# %%
if os.uname().nodename == 'madMacBook':  # a switch for the development environment
    from spike.Interactive import INTER
    INTER.hidecode(initial='hide', message=False)

# %% [markdown]
# #### *This program is still in development* -- *Please signal any problem while using it*
# We're working on it !

# %%
import EUFT_Spike.Tools.FTICR2D_INTER as IF2
from EUFT_Spike.Tools import DocEUFT
DocEUFT.Howto_display('2D')

# %%
from importlib import reload  # the two following lines are debugging help
reload(IF2)                   # and can be removed safely when in production
mr = IF2.MS2Dscene(Debug=False)


# %%
#mr.MR2D.diag.axis1.mass_axis()

# %%
DocEUFT.doc_display(doctype='2D')  # Show full doc

# %%
DocEUFT.sign()
