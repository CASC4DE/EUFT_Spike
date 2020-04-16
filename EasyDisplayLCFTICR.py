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
# ### *EU-FTICR-MS Network*
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
from importlib import reload  # the two following lines are debugging help
reload(LCI)                   # and can be removed safely when in production
mr = LCI.MS2Dscene(Debug=False)
#ms = LCI.MR_interact('FTICR_DATA/output.msh5', report=True, show=False, figsize=(8,6))

# %% [raw]
# from importlib import reload  # the two following lines are debugging help
# reload(LCI)                   # and can be removed safely when in production
# LCI.FI.injectcss()
# m1 = LCI.LC1D(ms,show=True)

# %%
# improve display of docu.
from IPython.display import display, Markdown
import ipywidgets as widgets
def dodoc(md):
    out = widgets.Output()
    with out:
        display(Markdown(md))
    return out
doc = dodoc('''# DOCUMENTATION

This program allows to analyse **LC-MS FTICR** data-sets, i.e. a series of MS spectra acquired during a chromatography run.
The information id bi-dimensional, with one chromatographic axis and one MS axis.

It is based on the [Spike](https://forum.casc4de.eu/p/2-spike) processing program,
the [scientific python](https://www.scipy.org/) language,
the [Jupyter](https://jupyter.org/) graphic environment,
and the [Voilà](https://github.com/voila-dashboards/voila) dashboard system.

The program allows to look at the whole data at once, as well as extracting MS spectra at a given retention time,
or a chromatogram extracted at a given *m/z*.

The raw data *(series of transients)* has to be processed before being handled here.
The processing  is performed in background on the deposit system,
expect a few hours for the processing to be performed.
There is no theoretical limit on the size of the data-set to process and visualize. 
The result of the processing is stored in a `*.msh5` file with the same filename than the Bruker directory.
These files use the standard 
[HDF5 format](https://www.hdfgroup.org/solutions/hdf5), and can be read with any program able to access this format.

Only files in the seafile deposit can be handled.

## Standard Operation:
#### Choose a file
LC-MS raw data are stored in the `ser` file in Bruker directories.
They have to be processed before being visualized with this utility.

Use  the selector to choose a `.msh5` file to display. 

#### Load
The 
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >Load</button>
button will get the processed experiment and display it.

**Warning** for the moment this tool present all `*.msh5` files rather than only the LC-MS files. - this will be solved soon -

#### Peak Pick
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >Peak Pick</button>
Will compute the Peak list, according to the parameters define in the "Processing Parameters" pane.

*This tool is not active and still in development*

## display
Figures can be explored *(zoom, shift, resize, etc)* with the jupyter tools displayed vertically.

The drawing zone can be resized using the little grey triangle on the lower-right corner

Figures can also be saved as a `png` graphic file.

## Panes
#### 1D Extraction
Extract of the experiment can be displayed here, 

- On the **MS** line click on 
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >get</button>
to get a MS spectra extracted at the retention time
    given by the slider - labelled in minutes *(you can also type the value)*
- On the **LC** line click on
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >get</button>
to get a chromatogram of the *m/z* peak location given by the slider *(you can also type the value)*
    - if needed the chromatogram can be smoothed for better looking.
- both extractions can be summed other a small region around the given location - which width is given by the second slider.

#### 2D spectrum:
A 2D view of the LC-MS experiment,
- To speed-up the display, a low resolution of the spectrum is displayed
  when a large zone of the experiment is displayed.
- resolution is udapted after zooming-in

#### Peak list
the peak list, if computed - can be exported in csv format

*This tool is not active and still in development*

#### Processing Parameters
all the parameters used for the processing

*This tool is not active and still in development*

#### Info
Details on the experiment.
In particular the different resolutions layered in the document are presented.

## Calibration
The calibration used by SPIKE is based on a 2 or 3 parameters equation :

*f = A / (m/z) - B + C / (m/z)²*

where *A* *B* and *C* are imported from the Bruker `ML1` `ML2` `ML3` parameters.

**Be carefull** Bruker uses a sign inversion on `ML2` depending on the value of `ML3` - this is not used, and the equation is allwas the same.

This set-up will be changed in the future for a more flexible and robust set-up
''')

comment = dodoc('''## *comments*

This is a temporary version.

expect improvements, as certain parts are still in development
- precise *m/z* calibration
- better user interaction
- more efficient peak-picking
- export to mzml and csv
- 3D view of the experiment
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
- pb d'axe de la projection
- doit et automation

### to come
- changer le selecteur
- changer l'affichage
    - LC horiz ?
    - 3D ?
- extraction of 1D 
    - titre Tic
    - Pmax ?
    - extraction - case editable pour les valeurs
    - multimanipe
    - affichage courbe / zones colorées
- NO DATA qui reste

https://mzmine.github.io/

### pour bientôt
- calibration
- peak detection
'''

