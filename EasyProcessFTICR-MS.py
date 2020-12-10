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

info = dodoc(FI.about())
doc = dodoc('''# DOCUMENTATION


This program allows to process and analyze **MS FTICR** data-sets, i.e. raw transients
as obtained from the FTICR machine.

The program allows to process transients, detect peaks, interact with the spectrum,
and store the final result.
A signed audit travail of the processing is maintained, in order to insure a complete reproducibility of the process.

There is no theoretical limit on the size of the data-set to process and visualize. 

The result of the processing is stored in a `*.msh5` file with the same filename than the Bruker directory.
These files use the standard 
[HDF5 format](https://www.hdfgroup.org/solutions/hdf5), and can be read with any program able to access this open format.

Only files in the seafile deposit can be handled.

Simply close the window to exit the program

## Standard Operations:
#### Choose a file
Only files in the SeaDrive deposit can be handled.
Use  the selector to choose an experiment.
Bruker `experiment.d` contains the raw transiens, and `.msh5` files are previously processed an stored data.

#### Load
The 
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >Load</button>
button will get the transient of the  selected experiment and display it.
Any previous processing will be lost

#### Process
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >Process</button>
 computes the Spectrum, according to the parameters define in the `Processing Parameters` panel

#### Peak Pick
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >Peak Pick</button>
 computes the Peak list, according to the parameters define in the `Processing Parameters` panel

#### Save
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >Save</button>
stores a `.msh5` file into the initial `experiment.d` firectory

#### Exit
Simply close the window to exist the program

## Tab Panels
- `raw fid`: the transient, if loaded
- `Spectrum`: the processed spectrum, if computed
- `Peak list`: the peak list, if computed - is also exported in csv format into the dataset directory
- `Processing Parameters`: all the parameters used for the processing: 
- `Info`: details on the experiment and Processing audit trails

## display
Figures can be interactively explored with the jupyter tools displayed  on the side of the dataset.

- zoom with <button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Zoom to rectangle" style="outline: currentcolor none medium;"><i class="center fa fa-square-o"></i></button>
- shift and resize
<button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Pan axes with left mouse, zoom with right" style="outline: currentcolor none medium;"><i class="center fa fa-arrows"></i></button>
 (with left and right click)
- <button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Back to previous view" style="outline: currentcolor none medium;"><i class="center fa fa-arrow-left"></i></button>
and
<button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Forward to next view" style="outline: currentcolor none medium;"><i class="center fa fa-arrow-right"></i></button>
allow to navigate in the zoom history

The drawing zone can be resized using the little gray triangle on the lower-right corner

Figures can also be saved as a `png` graphic file with
<button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Download plot" style="outline: currentcolor none medium;"><i class="center fa fa-floppy-o"></i></button>

## Processing Parameters
A few processing parameters can be adapted:
- **center fid**:    default: Yes <br>
  because of an eventual offset in the electronic, the experimental 'FID' might not be centered
  on the null value, but on some artefactual value.
  Removing this artefact before Fourier Transform may improve the spectral quality
- **apod todo**: default: hamming <br>
  The choice of the apodisation (windowing) function:
    - hamming: provides good resolution and SNR at the price of wiggles at the feet of large peaks
    - hanning: provides low wiggles at the price of lower resolution and SNR
    - kaiser: a family of parametric windows of optimized apodisation, 
        - 3.5: best possible resolution and SNR at the price of wiggles at the feet of large peaks
        - 5: Similar to Hamming
        - 6: Similar to Hanning
        - 8: very low wiggles, for resolution and SNR close to Hanning
- **baseline todo**: default: offset<br>
    removes the offset on the final spectrum 
- **grass noise todo**: default: "Only when storing file"<br>
    Set points below a certain level (see grass noise level below) to zero.
    Allows to efficiently compress saved dataset, but looses information 
- **grass noise level**: default: 3.0<br>
    the level for "grass noise" removal is taken as the standard deviation of the baseline signal ( 𝜎 )
    multiplied by this coefficient. So default is 3𝜎.
- **peakpicking**: default: Manually<br>
    when to do peak picking, on demand or automatically after FT
- **peakpicking noise level**: default: 10.0<br>
    when doing peak picking, all peaks above a threshold expressed as a ratio above the noise level 𝜎 is detected.
    so default is 10𝜎 (which is quite low).
- **centroid**: default: No<br>
    after peak picking, a centroid is computed, it permits to improve the value of the position, and estimates its width.
- **max peak disp**: default: 200<br>
    when many peaks are detected, the display of all the peaks becomes very slow, so only this many peaks 
    are shown, showing only the highest peaks. Will be redisplayed for each new zoom window.
    To adapt to your local set-up.

## Calibration
The calibration used by SPIKE is based on a 2 or 3 parameters equation :

*f = A / (m/z) - B + C / (m/z)²*

where *A* *B* and *C* are imported from the Bruker `ML1` `ML2` `ML3` parameters.

**Be carefull** Bruker uses a sign inversion on `ML2` depending on the value of `ML3` 
- this is not used, and the equation is allways the same.

This set-up will be changed in the future for a more flexible and robust set-up
''')

comment = dodoc('''## *comments*

This is a temporary version.

expect improvements, as certain parts are still in development
- precise *m/z* calibration
- more efficient peak-picking
- export to mzml
- superimposition of several spectra
- storage of the audit-trail
- ...
''')

accordion = widgets.Accordion(children=[info, doc, comment])
accordion.set_title(0,'About')
accordion.set_title(1,'Documentation')
accordion.set_title(2,'Comments')
accordion.selected_index = None
accordion

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

to do:
- export to mzml
- peak list
- superimposition
- simple A B C calibration
"""
