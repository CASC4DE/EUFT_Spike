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
# # Processing and Analysis of MS FTICR data

# %%
# adapt sys.path to local env
import sys, os
if os.uname().nodename == 'madMacBook':  # a switch for the development environment, add yours if need be
    print('on my Mac')
    os.chdir('..')
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

# %%
import EUFT_Spike.Tools.FTICR_INTER as FI
from EUFT_Spike.Tools import DocEUFT
DocEUFT.Howto_display('1D')


# %%
# launch
#display(Markdown('## ... program is Ready'))
#I.hidecode(initial='show', message=False)
from importlib import reload
reload(FI)
w = FI.IFTMS()

# %% [markdown]
# ---

# %%
DocEUFT.doc_display(doctype='1D')  # Show full doc

# %%
a_FAIRE = """
beta:
- marge metadata
- upload ,?
- pp q plante ? (scr dump)
- zf 2 et pp level 30 par défaut
- ordre voilà antialphab
- close to exit
- "panels" / tabs ,
- INFO pour les 1D msh5

to do:
- export to mzml
- peak list
- superimposition
- simple A B C calibration
"""

# %%
DocEUFT.sign()
