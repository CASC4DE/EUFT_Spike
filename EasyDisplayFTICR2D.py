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
# We're still working on it !

# %%
from IPython.display import display, Markdown
import ipywidgets as widgets
def dodoc(md):
    out = widgets.Output()
    with out:
        display(Markdown(md))
    return out
howto = dodoc("""
## 2D processing
In order to appear here, 2D-MS experiments have to be processed.
We're working on installing 2D processing here, however, this is not fully available yet.
In the mean time, process your 2D locally *as usual*, and drop the processed file in the `.d` folder of the experiment, it will show up in the chooser.
""")
rajout="""

In order to appear here, 2D-MS experiments have to processed in the background before being displayed on this tool.
First be sure that the `xxx.d` folder contains all the required raw data (the `ser` and `scan.xml` files), and the `*.m` folder with the method parameters.

Then, you should upload into the Bruker `xxx.d` folder a configuration file called 
`process2D_yyy.mscf` where `yyy` can be anything (the name is important, the processing program search for it using this pattern).

If you wish, you can use the [online tool](http://10.18.0.2:5052/BLABLA)
to prepare such a file, eventually edit it (it is a simple text file)
then upload it to the directory.

The presence of such a file will trigger the background processing, and your processed dataset will appear in the list.
If different  `process2D_yyy.mscf` files are present, respective processings will be performed.

Depending on the processing parameters, the size of 2D dataset, and the server load, the processing can take
from one hour to more than a day.
"""
acc2 = widgets.Accordion(children=[howto,])
acc2.set_title(0,'How to handle 2D-MS experiments')
acc2.selected_index = None
acc2

# %%
import EUFT_Spike.Tools.FTICR_INTER as FI
import EUFT_Spike.Tools.FTICR2D_INTER as IF2

# %%
from importlib import reload  # the two following lines are debugging help
reload(IF2)                   # and can be removed safely when in production
mr = IF2.MS2Dscene(Debug=False)


# %%
#mr.MR2D.diag.axis1.mass_axis()

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

This program allows to analyse **2D-MS FTICR** data-sets.

Only files in the Seafile deposit can be handled.

Select the file you want look at, and Load, it will show-up as a full width 2D image.

## 2D Spectrum

Is shown as a full width 2D image.

- the F2/horizontal axis is the high resolution, direct axis. You find fragment ions along this line
- the F1/vertical axis indirect axis, usually at lower resolution. You have parent ions along this axis. 
- the top and right spectra show the diagonal of the experiment *( m/z<sub>F1</sub> = m/z<sub>F2</sub> )* .
it should be equivalent to the complete parent + fragment spectrum.

What you are seeing is the contour plot of the 2D experiment. 

> *Think of the experiment like a landscape filled with water (an archipelago of small islands),
> and your seeing a map of this continuous landscape.
> If a dot appears, it means that it is higher than the sea level.*

- with the `scale` slider, you can select the levels at which the contours are drawn.
    - *(you raise or lower the sea "level"*)
    - `Reset` gets back to 1.0
    - `Redraw` is sometime needed and recompute the map
- `Side spectra scale` changes the size of the side spectra
- you can zoom by dialing limit values in the `Zoom Box` 
- `Highest displayed mass` limit the highest displayed mass in the zoom box
- or with the interactive tools (the bar left to the spectrum)
    - zoom with <button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Zoom to rectangle" style="outline: currentcolor none medium;"><i class="center fa fa-square-o"></i></button>
    - shift and resize
    <button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Pan axes with left mouse, zoom with right" style="outline: currentcolor none medium;"><i class="center fa fa-arrows"></i></button>
     (with left and right click)
    - <button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Back to previous view" style="outline: currentcolor none medium;"><i class="center fa fa-arrow-left"></i></button>
    and
    <button class="jupyter-matplotlib-button jupyter-widgets jupyter-button" href="#" title="Forward to next view" style="outline: currentcolor none medium;"><i class="center fa fa-arrow-right"></i></button>
    allow to navigate in the zoom history


- The data have a hierarchical multiresolution structure. When zooming,
the `Redraw` button loads the version of the data with the optimal resolution.
The smaller the zoom box, the better the resolution.
`#1` means you have the full resolution, higher numbers are lower resolution.

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

*full doc to be written - sorry*

#### Peak list
is not active yet.

#### Info
Display details on the experiment.
In particular the different resolutions layered in the document are presented.

## Standard Operation:
#### Choose a file
2D-MS raw data are stored in the `ser` file in Bruker directories.
They have to be processed before being visualized with this utility.

The selector will present only those `.msh5` files which are available for analysis.

There is no limit on the size of the dataset to be explored.

#### Explore the experiment in 2D mode
Using the interactive tools available in the 2D panel (see above)

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

comment = dodoc('''
This is a temporary version.

expect improvements, as certain parts are still in development
- 2D processing
- precise *m/z* calibration
- better user interface
- 2D peak-picking detection
- locate/remove artifacts due to harmonics
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
print('spike version:',spike.version.version)
print('interface version:',FI.version)
