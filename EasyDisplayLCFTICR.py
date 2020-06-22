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
# adapt sys.path to local env
import sys, os
if os.uname().nodename == 'madMacBook':  # a switch for the development environment
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
from IPython.display import display, Markdown
import ipywidgets as widgets
def dodoc(md):
    out = widgets.Output()
    with out:
        display(Markdown(md))
    return out
howto = dodoc("""
In order to appear here, LC-MS experiments have to processed in the background before being displayed on this tool.
First be sure that the `xxx.d` folder contains all the required raw data (the `ser` and `scan.xml` files), and the `*.m` folder with the method parameters.

To do so, you should upload into the Bruker `xxx.d` folder a configuration file called 
`import_yyy.mscf` where `yyy` can be anything (the name is important, the processing program search for it using this pattern).

You can [download here](http://10.18.0.2:5052/static/import_default.mscf) a template file, eventually edit it (it is a simple text file) it and upload it to the directory.
The presence of such a file will trigger the background processing, and your processed dataset will appear in the list.
If different  `import_*.mscf` files are present, respective processings will be performed.


For more information see `Documentation` below.
""")
acc2 = widgets.Accordion(children=[howto,])
acc2.set_title(0,'How to process LC-MS experiments')
acc2.selected_index = 0
acc2

# %%
import EUFT_Spike.Tools.LCFTICR_INTER as LCI
#print('spike version:',spike.version.version)
#print('interface version: ',LCI.FI.version)

# %%
from importlib import reload  # the two following lines are debugging help
reload(LCI)                   # and can be removed safely when in production
mr = LCI.MS2Dscene(Debug=False)

# %%
# improve display of docu.
from IPython.display import display, Markdown
import ipywidgets as widgets
def dodoc(md):
    out = widgets.Output()
    with out:
        display(Markdown(md))
    return out

info = dodoc(LCI.FI.about())
doc = dodoc('''# DOCUMENTATION

This program allows to analyse **LC-MS FTICR** data-sets, i.e. a series of MS spectra acquired during a chromatography run.
The information is bi-dimensional, with one chromatographic axis and one MS axis.

The program allows to look at the whole data at once, as well as extracting MS spectra at a given retention time,
or a chromatogram extracted at a given *m/z*.

The raw data `ser` *(series of transients)* has to be processed before being handled here.
The processing  is performed in background on the deposit system,
expect a few hours for the processing to be performed.
There is no theoretical limit on the size of the data-set to process and visualize. 
The result of the processing is stored in a `*.msh5` file with the same filename than the Bruker directory.
These files use the standard 
[HDF5 format](https://www.hdfgroup.org/solutions/hdf5), and can be read with any program able to access this open format.

Only files in the Seafile deposit can be handled.

## Spectra
Spectra can be interactively explored with the jupyter tools displayed  on the side of the dataset.

- zoom with <button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Zoom to rectangle" style="outline: currentcolor none medium;"><i class="center fa fa-square-o"></i></button>
- shift and resize
<button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Pan axes with left mouse, zoom with right" style="outline: currentcolor none medium;"><i class="center fa fa-arrows"></i></button>
 (with left and right click)
- <button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Back to previous view" style="outline: currentcolor none medium;"><i class="center fa fa-arrow-left"></i></button>
and
<button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Forward to next view" style="outline: currentcolor none medium;"><i class="center fa fa-arrow-right"></i></button>
allow to navigate in the zoom history

The drawing zone can be resized using the little grey triangle on the lower-right corner

Figures can also be saved as a `png` graphic file with
<button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Download plot" style="outline: currentcolor none medium;"><i class="center fa fa-floppy-o"></i></button>

## Tab Panels
There several tab panels that play different roles

#### 1D Extraction
Slices from the complete experiment can be computed and displayed here, 

- On the **MS** line click on 
<button class="p-Widget jupyter-widgets jupyter-button widget-button" style="width: 60px;">get</button>
to get a MS spectra extracted at the retention time
    given by the slider - labelled in minutes *(you can also type directly the value)*.
- On the **LC** line click on
<button class="p-Widget jupyter-widgets jupyter-button widget-button" style="width: 60px;">get</button>
to get a chromatogram of the *m/z* peak location given by the slider *(you can also type directly the value)*.
If needed the chromatogram can be smoothed for better looking using a Savitsky-Golay method - 0 means no smoothing.
- both extractions can be summed other a small region around the given location - which width is given by the second slider.

for both type of dataset, the 
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >Peak Pick</button> button
computes the position of peaks of the dataset currently displayed, and stores it as a CSV file in the project folder.

The 
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >Save</button> button
stores the content of the window, as a `.msh5` file for MS spectra or in CSV format for chromatograms.


#### 2D spectrum:
A 2D view of the LC-MS experiment, displayed as a contour map.

To speed-up the display, a low resolution of the spectrum is displayed
  when a large zone of the experiment is displayed, resolution is optimized after zooming-in.
The resolution being used is displayed on the top left of the 2D map,
(see in the `Info` Panel for the different resolution of the dataset.)
and R is an estimate of the maximum resolving power available in the center of the zoom window
(computed from the sampling of the *m/z* axis rather than from the actual peak width!).

The zoom box on the top shows the current zoom limits, which can be modified at will.
The 
<button class="p-Widget jupyter-widgets jupyter-button widget-button">Apply</button> button 
activates the entry.

The vertical slider chooses the values at which the levels are drawn, and the 
<button class="p-Widget jupyter-widgets jupyter-button widget-button" style="width: 80px;">Redraw</button> and 
<button class="p-Widget jupyter-widgets jupyter-button widget-button" style="width: 80px;">Reset</button> buttons
will recompute the display, `Redraw` with the current zoom and scale parameters, and `Reset` with the default parameters.

#### Peak list
Display the last computed peak list from the 1D panel.

#### Info
Display details on the experiment.
In particular the different resolutions layered in the document are presented.


## Standard Operation:
#### Choose a file
LC-MS raw data are stored in the `ser` file in Bruker directories.
They have to be processed before being visualized with this utility.

The selector will present only those `.msh5` files which are available for analysis.

There is no limit on the size of the dataset to be explored.
*During the development, tests where performed on a 1800 × 4096k experiment (1800 spectra of 4096k length)
and the program was reasonably swift.*

#### Explore the experiment in 2D mode
Using the interactive tools available in the 2D panel (see above)

The TIC profile on the right and the MS total spectrum on the top allow to precisely locate the signals of interest.

#### Extract spectra and chromatogram
Using the 1D panel, you can look at a MS spectrum for a given retention time;
or extract a chromatographic profile associated to a *m/z* value, or a range of values.

You can realize a pick-peaking as well as store the displayed dataset.

`.msh5` files created from the MS spectra stored with this tool can then loaded back into the program `Process_Tool`.

#### Exit
Simply close the window to exit the program


## Calibration
The calibration used by SPIKE is based on a 2 or 3 parameters equation :

*f = A / (m/z) - B + C / (m/z)²*

where *A* *B* and *C* are imported from the Bruker `ML1` `ML2` `ML3` parameters.

**Be careful** Bruker uses a sign inversion on `ML2` depending on the value of `ML3` -
this is not used, and the equation is always the same.

This set-up will be changed in the future for a more flexible and robust set-up
''')

comment = dodoc('''## *comments*

This is a temporary version.

expect improvements, as certain parts are still in development
- precise *m/z* calibration
- better user interaction
- more efficient peak-picking
- export and comparison of spectra
- export to mzml and csv
- real 3D view of the experiment
- ...
''')

accordion = widgets.Accordion(children=[info, doc, comment])
accordion.set_title(0,'About')
accordion.set_title(1,'Documentation')
accordion.set_title(2,'Comments')
accordion.selected_index = None
accordion

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
print('spike version:',spike.version.version)
print('interface version - ',LCI.FI.version)
