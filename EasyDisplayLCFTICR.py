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
### Initialization of the environment
### the following cell should be run only once *(but no harm if you run it twice)* .

from IPython.display import display, HTML, Markdown, Image
display(Markdown('## STARTING Environment...'))
# %matplotlib widget
import spike
from spike.Interactive.INTER import hidecode
import LCFTICR_INTER as IF2
display(Markdown('## ... program is ready'))
from importlib import reload  # the two following lines are debugging help
reload(IF2)                   # and can be removed safely when in production
ms = IF2.MS2Dscene(root='.')

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

# %%
for i,dl in enumerate( ms.MR2D.data):
    print (dl.axis1.stoi(60))
    print (dl.axis1.report())
#ms.MR2D.min

# %%
mr = IF2.MR('./LCMS-FTICRtest.msh5')

# %%
mr.data[0].axis1.currentunit
mr.data[0].axis1.ctoi(10.3)
mr.data[0].axis1.Tmin

# %%
mr.data
for i,dl in enumerate(mr.data):
    mr.data[i].axis1 = TimeAxis(size=sizeF1, tabval=np.array(mr.min), importunit="min", currentunit='min' )  

# %%
1763//881

# %%
mr.data[6]

# %%
mr.data[7].axis1.currentunit = 'sec'

# %%
import matplotlib.pyplot as plt
with ms.out2D:
    plt.plot([1,2,3],[2,4,0])

# %%
with ms.out2D:
    IF2.MR_interact(ms.FC.selected,  show=True, figsize=(8,8), Debug=False)

# %%
IF2.MR_interact(ms.FC.selected,  show=True, figsize=(8,8), Debug=False)

# %%
