#!/usr/bin/env python 
# encoding: utf-8
"""
Contains Documentation and other Markdown for EU_FTICR set of prgms
"""
from IPython.display import display, Markdown
import ipywidgets as widgets
import spike
from . import FTICR_INTER as FI


def sign():
    print('spike version:',spike.version.version)
    print('interface version - ',FI.version)


# improved display of docu.
def dodoc(md):
    out = widgets.Output()
    with out:
        display(Markdown(md))
    return out

info = dodoc(FI.about())

#################### 1D 
Howto1D = """
## This program is for processing, display and interaction of single FTICR-MS experiments

In order to appear here, the FTICR experiment should have been deposited on the Seafile repository.
Drop there the complete  `*.d` directory. 
Most the files and subdirectory are needed for proper processing, except maybe the `*.baf` files
which will not used here.

For more information see `Documentation` below.
"""

D1D = '''
# This program

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

# Standard Operations:
### Choose a file
Only files in the SeaDrive deposit can be handled.
Use  the selector to choose an experiment.
Bruker `experiment.d` contains the raw transiens, and `.msh5` files are previously processed an stored data.

### Load
The 
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >Load</button>
button will get the transient of the  selected experiment and display it.
Any previous processing will be lost

### Process
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >Process</button>
 computes the Spectrum, according to the parameters define in the `Processing Parameters` panel

### Peak Pick
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >Peak Pick</button>
 computes the Peak list, according to the parameters define in the `Processing Parameters` panel

### Save
<button class="p-Widget jupyter-widgets jupyter-button widget-button" >Save</button>
stores a `.msh5` file into the initial `experiment.d` firectory

### Exit
Simply close the window to exist the program

## Tab Panels
- `raw fid`: the transient, if loaded
- `Spectrum`: the processed spectrum, if computed
- `Peak list`: the peak list, if computed - is also exported in csv format into the dataset directory
- `Processing Parameters`: all the parameters used for the processing: 
- `Info`: details on the experiment and Processing audit trails

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

'''

################### LC
HowtoLC = """
## This program is for  display and interaction of LC-coupled FTICR-MS experiments.

In order to appear here, LC-MS experiments have to processed in the background before being displayed on this tool.
First be sure that the `xxx.d` folder contains all the required raw data (the `ser` and `scan.xml` files), and the `*.m` folder with the method parameters.

To do so, you should upload into the Bruker `xxx.d` folder a configuration file called 
`import_yyy.mscf` where `yyy` can be anything (the name is important, the processing program search for it using this pattern).

You can [download here](http://10.18.0.2:5052/static/import_default.mscf) a template file, eventually edit it (it is a simple text file) it and upload it to the directory.
The presence of such a file will trigger the background processing, and your processed dataset will appear in the list.
If different  `import_*.mscf` files are present, respective processings will be performed.

For more information see `Documentation` below.
"""

DLC = '''
# This program

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

'''
############################ 2D
Howto2D = """
## This program is for  display and interaction of 2D-FTICR-MS experiments

In order to appear here, 2D-MS experiments have to be processed.
We're working on installing 2D processing here, however, this is not fully available yet.
In the mean time, process your 2D locally *as usual*, and drop the processed file in the `.d` folder of the experiment, it will show up in the chooser.
"""

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

D2D = """
# This Program

This program allows to analyse **2D-MS FTICR** data-sets.
Only processed 2DMS files in the Seafile deposit can be handled.

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

The data has a hierarchical multiresolution structure. When zooming,
the `Redraw` button loads the version of the data with the optimal resolution.
The smaller the zoom box, the better the resolution.
`#1` means you have the full resolution, higher numbers are lower resolution.

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

"""
############################### General
Calibration = '''# Calibration
The calibration used by SPIKE is based on a 2 or 3 parameters equation :

*freq = A / (m/z) - B + C / (m/z)²*

where *A* *B* and *C* are imported from the Bruker `ML1` `ML2` `ML3` parameters.

**Be carefull** Bruker uses a sign inversion on `ML2` depending on the value of `ML3` 
- this is not used, and the equation used for calibration is allways the eq above, even if C is 0.

Nevertheless, the equation above is not optimal, and unstable in certain conditions.
We are working on a better definition, which will allow more robust calibrations and
this set-up will be changed in the future for a more flexible and robust set-up

'''

Display = '''
# Display

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
'''

comment = dodoc('''
This is a preliminary version.

expect improvements, as certain parts are still in development
- precise *m/z* calibration
- better user interaction
- more efficient peak-picking
- export to mzml
- comparison of several spectra
- storage of the audit-trail
- real 3D view of the LC and 2D experiments

''')

def doc_display(doctype='1D'):
    "create nice markdown doc, doctype can be '1D', '2D', 'LC'"
    if doctype == '1D':
        doc = dodoc(D1D + Display + Calibration)
    elif doctype == 'LC':
        doc = dodoc(DLC + Display + Calibration)
    elif doctype == '2D':
        doc = dodoc(D2D + Display + Calibration)
    else:
        doc = dodoc("\n## *missing documentation*\n")
    accordion = widgets.Accordion(children=[info, doc, comment])
    accordion.set_title(0,'About')
    accordion.set_title(1,'Documentation')
    accordion.set_title(2,'Comments')
    accordion.selected_index = None
    return accordion


def Howto_display(doctype='1D'):
    "create nice markdown howto,  doctype can be '1D', '2D', 'LC'"
    if doctype == '1D':
        how = dodoc(Howto1D)
    elif doctype == 'LC':
        how = dodoc(HowtoLC)
    elif doctype == '2D':
        how = dodoc(Howto2D)
    else:
        how = dodoc("\n## *missing documentation*\n")
    acc2 = widgets.Accordion(children=[how,])
    acc2.set_title(0,'How-to ...')
    acc2.selected_index = None
    return acc2
