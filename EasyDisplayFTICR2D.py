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
if os.uname().nodename == 'madMacBook':  # a switch for the development environment
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

# %%
from IPython.display import display, Markdown
import ipywidgets as widgets
def dodoc(md):
    out = widgets.Output()
    with out:
        display(Markdown(md))
    return out
howto = dodoc("""
### *This program is still in development* -- *Please signal any problem while using it*
We're still working on it !

## 2D processing
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

## Usage of the display tool
- select the file you want look at, and Load, it will show-up as a full width 2D image.
*ignore eventual warnings about missing attributes*
    - the F2/horizontal axis is the high resolution, direct axis. You find fragment ions along this line
    - the F1/vertical axis indirect axis, usually at lower resolution. You have parent ions along this axis. 
- with the zoom tool (the square below the spectrum) you can select the region you want to display,
  you can also dial it in on the top box.
- with the `scale` slider, you can select the display level.
*Think to this as an archipelago viewed on the map; the slider changes the sea level, raising the scale raises the floor (or lower the sea level)*
- The data have a hierarchical multiresolution structure. When zooming,
the `Redraw` button loads the version of the data with the optimal resolution.
The smaller the zoom box, the better the resolution.

### to come next
expect improvements, as certain parts are still in development
- precise *m/z* calibration
- better user interaction
- 2D peak-picking detection
- extraction of arbitrary 1D (vertical, horizontal and diagonal)
- locate/remove artifacts due to harmonics
- export and comparison of spectra
- export to mzml and csv
- real 3D view of the experiment
- ...
""")
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
from  spike.FTICR import FTICRData
def _get_diagonal(data):
    ddiag = data.row(0)
    diag =  np.zeros(data.size2)
    for i in range(data.size2):
        mz  = data.axis2.itomz(i)
        diag[i] = data[int(round(data.axis1.mztoi(mz))),  int(round(data.axis2.mztoi(mz)))]
    ddiag.set_buffer(diag).plus()
    return ddiag
def get_diagonal(data):
    ddiag = data.row(0)
    diag =  np.zeros(data.size2)
    mz  = data.axis2.mass_axis()
    iz = np.int_(np.round(data.axis1.mztoi(mz)))
    jz = np.int_(np.round(data.axis2.mztoi(mz)))
    diag = data[iz,jz]
    ddiag.set_buffer(diag).plus()
    return ddiag
#get_diagonal(mr.MR2D.data[0]).set_unit('m/z').display()
#_get_diagonal(mr.MR2D.data[1]).set_unit('m/z').display(new_fig=False)
"""  timings
- 0  : 93++   8.3
- 1 : 5.40    0.59
- 2 : 1.41    0.1
- 3 : 0.4
""";
