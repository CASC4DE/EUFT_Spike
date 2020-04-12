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

# %%
import Tools.LCFTICR_INTER as LCI

# %%
# improve display
from IPython.display import display, HTML, Javascript, Markdown
from ipywidgets import interact, fixed, HBox, VBox, GridBox, Label, Layout, Output, Button
import ipywidgets as widgets

display(HTML('<style>hr {height: 2px; border: 0;border-top: 1px solid #ccc;margin: 1em 0;padding: 0; }</style>'))
def dodoc(md):
    out = Output()
    with out:
        display(Markdown(md))
    return out


# %%
from importlib import reload  # the two following lines are debugging help
reload(LCI)                   # and can be removed safely when in production
#mr = LCI.MS2Dscene()
ms = LCI.MR_interact('FTICR_DATA/output.msh5', report=False,show=True, figsize=(8,6))

# %%
ms.log

# %%
ms.fig.canvas

# %%
LCI.different(1,1.011)

# %%
ms.show()

# %%
doc = dodoc('''# DOCUMENTATION

## display
Figures can be explored *(zoom, shift, resize, etc)* with the jupyter tools displayed  below the dataset.


The drawing zone can be resized using the little grey triangle on the lower-right corner

Figures can also be saved as a `png` graphic file.

## Standard handling:
#### Choose a file
LC-MS raw data are stored in the `ser` file in Bruker directories.
They have to be processed before being visualized with this utility.
The processing  is performed in background on the deposit system, expect a few hors for the processing to be performed.
The result of the processing is stored in a `*.msh5` file file the same filename than the bruker directory.
Only files in the seafile deposit can be handled.

Use  the selector to choose a `msh5` file to display. 

#### Load
The `Load` button will get the processed experiment and display it.

#### Peak Pick
Will compute the Peak list, according to the parameters define in the "Processing Parameters" pane

## Panes
- 1D Display: Extract of the experiment can be displayed here, 
    - MS spectra at a given retention time
    - chromatogram at a given $m/z$
- 2D spectrum: A 2D display of the LC-MS experiment,
    - To speed-up the display, a low resolution of the spectrum is displayed
      when a large zone of the experiment is displayed.
    - resolution is udapted after zooming-in
- Peak list: the peak list, if computed - can be exported in csv format
- Processing Parameters: all the parameters used for the processing: 
- Info: details on the experiment

## Calibration
The calibration used by SPIKE is based on a 2 or 3 parameters equation :
$$
f = \frac{A}{m/z} - B + \frac{C}{(m/z)^2}
$$
where $A$ $B$ and $C$ are imported from the Bruker `ML1` `ML2` `ML3` parameters.

**Be carefull** Bruker uses a sign inversion on `ML2` depending on the value of `ML3` - this is not used, and the equation is allwas the same.

This set-up will be changed in the future for a more flexible and robust set-up
''')

comment = dodoc('''## *comments*

This is a temporary version.

expect improvements, as certain parts are still in development
- $m/z$ calibration
- more efficient peak-picking
- export to mzml
- ...
''')

accordion = widgets.Accordion(children=[doc, comment])
accordion.set_title(0,'Documentation')
accordion.set_title(1,'Comments')
accordion.selected_index = None
accordion

# %%
todo = '''# TODO
### importer
- 

### to come
- changer le selecteur
- mise à jour de la boite de zoom (easyDisplay2D)
- changer l'affichage
    - composite avec projection des axes (Proc2DNMR)
    - projection spectre MS ? (calculée en amont)
    - LC horiz ?
    - 3D ?
- extraction of 1D 
    - Tic
    - Pmax
    - 2 onglets 1D
        - à une masse donnée  ou un intervalle => chromatogramme
        - à un temps donné - ou un intervalle de temps => spectre masse
    - multimanipe
    - affichage courge / zones colorées

https://mzmine.github.io/

### pour bientôt
- calibration
- peak detection
'''


# %%
STOP

# %%
# ls FTICR_DATA/

# %%
from importlib import reload  # the two following lines are debugging help
reload(LCI)                   # and can be removed safely when in production
mr = LCI.MR_interact('FTICR_DATA/output.msh5', report=False,show=False)

# %%
mr.show

# %%
np.maximum(np.arange(10),np.arange(10,0,-1))

# %%
# np.maximum?

# %%
