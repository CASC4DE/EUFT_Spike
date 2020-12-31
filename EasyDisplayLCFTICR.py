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
# # Analysis of LC-MS FTICR data

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
# %matplotlib widget
# %xmode Plain
import spike


# %%
if os.uname().nodename == 'madMacBook':  # a switch for the development environment
    from spike.Interactive import INTER
    INTER.hidecode(initial='hide', message=False)

# %%
import EUFT_Spike.Tools.LCFTICR_INTER as LCI
from EUFT_Spike.Tools import DocEUFT
DocEUFT.Howto_display('LC')

# %%
from importlib import reload  # the two following lines are debugging help
reload(LCI)                   # and can be removed safely when in production
mr = LCI.MS2Dscene(Debug=False)

# %%
DocEUFT.doc_display(doctype='LC')  # Show full doc

# %%
todo = '''# TODO
### importer
- pp
    - parameter
    - audit
### to come
- changer l'affichage
    - LC horiz ?
    - 3D ?
- extraction of 1D 
    - titre Tic
    - Pmax ?
    - multimanipe
    - affichage courbe / zones colorées
- NO DATA qui reste

https://mzmine.github.io/

### pour bientôt
- calibration
- peak detection
'''


# %%
DocEUFT.sign()
