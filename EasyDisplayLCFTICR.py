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
# # Display utility for LC-MS FTICR Spectra
#
#

# %%
# %%capture
# %matplotlib widget
# %xmode Plain
import spike
import Tools.LCFTICR_INTER as LCI

# %%
from importlib import reload  # the two following lines are debugging help
reload(LCI)                   # and can be removed safely when in production
ms = LCI.MS2Dscene()

# %%
[d.absmax for d in ms.MR2D.data[::-1]]

# %%
import spike.FTICR as FTICR
import spike.File.HDF5File as H5
H5.HDF5File()

# %%
import tables
fname = 'FTICR_DATA/LCMS-FTICRtest.msh5'
hf = tables.open_file(fname,"r")
for group in hf.iter_nodes("/","Group"):
        print("GROUP",group._v_name)
        if group._v_name.startswith('resol'):
            axe = getattr(group,"axes")
            display(axe)

# %%
hf.root.generic_table

# %%
STOP
from importlib import reload  # the two following lines are debugging help
reload(IF2)                   # and can be removed safely when in production
ms = IF2._MS2Dscene(root='/')

# %% [markdown]
# # TODO
# ### importer
# - 
#
# ### to come
# - changer le selecteur
# - mise à jour de la boite de zoom (easyDisplay2D)
# - changer l'affichage
#     - composite avec projection des axes (Proc2DNMR)
#     - projection spectre MS ? (calculée en amont)
#     - LC horiz ?
#     - 3D ?
# - extraction of 1D 
#     - Tic
#     - Pmax
#     - 2 onglets 1D
#         - à une masse donnée  ou un intervalle => chromatogramme
#         - à un temps donné - ou un intervalle de temps => spectre masse
#     - multimanipe
#     - affichage courge / zones colorées
#
# https://mzmine.github.io/
#
# ### pour bientôt
# - calibration
# - peak detection
#
