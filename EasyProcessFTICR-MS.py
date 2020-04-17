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
# ### *EU-FTICR-MS Network*

# %%
# %%capture
# load all python and interactive tools
# %matplotlib widget
# %xmode Plain
# Plain or Minimal.
import spike


# %%
import Tools.FTICR_INTER as FI


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
# improve display of docu.
from IPython.display import display, Markdown
import ipywidgets as widgets
def dodoc(md):
    out = widgets.Output()
    with out:
        display(Markdown(md))
    return out
doc = dodoc('''# DOCUMENTATION


This program allows to process and analyse **MS FTICR** data-sets, i.e. raw transients
as obtained from the FTICR machine.

It is based on the [Spike](https://forum.casc4de.eu/p/2-spike) processing program,
the [scientific python](https://www.scipy.org/) language,
the [Jupyter](https://jupyter.org/) graphic environment,
and the [Voilà](https://github.com/voila-dashboards/voila) dashboard system.

The program allows process the transients, detect peaks, interact with the spectrum,
and store the final result.
A signed audit travail of the processing is maintained, in order to insure a complete reproducibility of the process.

There is no theoretical limit on the size of the data-set to process and visualize. 

The result of the processing is stored in a `*.msh5` file with the same filename than the Bruker directory.
These files use the standard 
[HDF5 format](https://www.hdfgroup.org/solutions/hdf5), and can be read with any program able to access this format.

Only files in the seafile deposit can be handled.

Simply close the window to exist the program

## Standard Operation:
#### Choose a file
Only files in the seafile deposit can be handled.
Use  the selector to choose an experiment.
Bruker `experiment.d` contains the raw transiens, and `.msh5` files are previously processed an stored data.

#### Load
The 
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >Load</button>
button will get the transient of the  selected experiment and display it.
Any previous processing will be lost

#### Process
<button class="p-Widget jupyter-widgets jupyter-button widget-button mod-success" >Process</button>
 computes the Spectrum, according to the parameters define in the `Processing Parameters` pane

#### Peak Pick
<button class="p-Widget jupyter-widgets jupyter-button widget-button mod-success" >Peak Pick</button>
 computes the Peak list, according to the parameters define in the `Processing Parameters` pane

#### Save
<button class="p-Widget jupyter-widgets jupyter-button widget-button mod-success" >Save</button>
stores a `.msh5` file into the initial `experiment.d` firectory

#### Exit
Simply close the window to exist the program

## Panes
- raw fid: the transient, if loaded
- spectrum: the processed spectrum, if computed
- Peak list: the peak list, if computed - can be exported in csv format
- Processing Parameters: all the parameters used for the processing: 
- Info: details on the experiment and Processing audit trails

## display
Figures can be explored *(zoom, shift, resize, etc)* with the jupyter tools displayed  below the dataset.

The drawing zone can be resized using the little grey triangle on the lower-right corner

Figures can also be saved as a `png` graphic file.

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
- more efficient peak-picking
- export to mzml and csv
- superimposition of several spectra
- storage of the audit-trail
- ...
''')

accordion = widgets.Accordion(children=[doc, comment])
accordion.set_title(0,'Documentation')
accordion.set_title(1,'Comments')
accordion.selected_index = None
accordion

# %%
a_FAIRE = """
beta:
- doc top niveau
- page home
- marge metadata
- upload ,?
- pp q plante ? (scr dump)
- zf 2 et pp level 30 par défaut
- ordre voilà antialphab
- close to exit
- "panels" / tabs ,

to do:
- export to mzml
- peak list
- superimposition
- simple A B C calibration
"""

# %%
print('spike version:',spike.version.version)
print('interface version - ',FI.version)
