#!/usr/bin/env python 
# encoding: utf-8

"""
A tool to display FT-ICR data-sets

to be embedded in jupyter notebook

MAD april 2020

This version requires ipympl (see: https://github.com/matplotlib/jupyter-matplotlib )
and the notebook to be opened with %matplotlib widget
"""
import os.path as op
from pathlib import Path
import traceback
import subprocess
import json
import tables
import matplotlib.pyplot as plt
from ipywidgets import interact, fixed, HBox, VBox, GridBox, Label, Layout, Output, Button
import ipywidgets as widgets
from IPython.display import display, Markdown, HTML, Image
import numpy as np

import spike
from spike import FTICR
from spike.NPKData import flatten, parsezoom
from spike.FTMS import FTMSData
from spike.FTICR import FTICRData
from spike.File import BrukerMS
from . import utilities as U


# Static info

# REACTIVE modify callback behavior
# True is good for inline mode / False is better for notebook mode
REACTIVE = True
HEAVY = False
DEBUG = False

BASE = 'FTICR_DATA'              # name of the 
SIZEMAX = 8*1024*1024        # largest zone to display
NbMaxDisplayPeaks = 200      # maximum number of peaks to display at once
version = "1.1.0"            # 1.1 for 2D-MS

def about():
    'returns the about string in Markdown'
    val = '''This set of programs is developed by [CASC4DE](https://www.casc4de.eu) and is based on 
on the following tools:
- the [Spike](https://forum.casc4de.eu/p/2-spike) processing program,
- the [scientific python](https://www.scipy.org/) language,
- the [Jupyter](https://jupyter.org/) graphic environment,
and the [Voilà](https://github.com/voila-dashboards/voila) dashboard system.

For questions and more information check the [dedicated forum](https://forum.casc4de.eu/t/eu-fticr-ms)

### Current Version
- spike version: {0}
- interface version: {1}
'''.format(spike.version.version, version)

    release = '''
### Release notes
- 1.1 - Dec 2020
    - First version with 2D-FTICR-MS
- 1.0.04 - 20 June 2020
    - improved documentation
- 1.0.03 - 5 June 2020
    - possibility to peak-pick spectra and chromatograms extracted from a LC-MS experiment
    - possibility to save spectra and chromatograms extracted from a LC-MS experiment
    - improved error messages in metadata generation
    - better handling of error on files
    - improved online documentation
- 1.0.02 - 23 May 2020
    - added this about page / release notes
    - better error messages
    - better audit trail for peak-picking
    - improved online documentation
    - corrected a bug while doing a peak-picking on stored datasets
- 1.0.01 - 18 May 2020
    - improved the file chooser, shows only relevent files
    - corrected a bug while saving processed spectra from the old "Apex0" format (with 'acqus' file)
- 1.0.0  - 28 Apr 2020  initial version

'''
    return val+release

# TOOLS FOR 1D FTICR

def injectcss():
    """inject css into the notebook
    - HR
    - buttons
    """
    display(HTML('''
    <style>
    hr {height: 2px; border: 0;border-top: 1px solid #ccc;margin: 1em 0;padding: 0; }
    .widget-button {
        width:100px;
        border:1px solid lightgray;
        border-radius:7px;
        box-shadow: 3px 3px 3px #666666;
        margin-right: 10px}
    </style>
    '''))

# modif dec 2020: File chooser tools
# A small object tto handle file lits
# The idea is to maintain the type of all datasets found in the user directory.
# Because the files may be over a slow file system (eg; FUSEd Seafile) 
#  a small db of file type is maintained.
#  currently a simple json file stored and retrieved
#  file dates insure data integrety

from collections import namedtuple
MSfile = namedtuple('MSfile',['fullpath', 'spath', 'ftype'])
MSfile.__doc__ = "a micro class for FileChooser"
# redefining __str__ for nicer display
def msstr(msf):
    return "%s \t \t %s"%(msf.ftype, msf.spath)
MSfile.__str__ = msstr

class File_list():
    def __init__(self, base='DATA', dotd=True, msh5=True,
                    accept=('fid', 'FID', 'ser', 'MS', 'LC-MS', '2D-MS')):
        self.base = base
        self.dotd = dotd
        self.msh5 = msh5
        self.accept = accept
        self.file_dico = self.build_dico()
        if DEBUG: print(len(self.file_dico.keys()))
        self._list = self.list_from_dico()
#        self._list = self.build_list()
    @property
    def list(self):
        return self._list
    def _filetype(self, path):
        """
        old version - VERY SLOW over seafile
        """
        if DEBUG: print('**filetype** path:',path, end=':')
        if path.suffix == '.d':
            if (path/'ser').exists():
                toreturn = 'ser'
            elif (path/'fid').exists():
                toreturn = 'fid'
            else:
                toreturn = '???'
        elif path.suffix == '.msh5':
            try:
                d = FTICRData(name=str(path), mode='onfile')
            except:
                return '???'
            if d.dim == 1:
                toreturn = 'MS'
            elif d.dim == 2:
                try:
                    pj = FTICRData(name=str(path), mode="onfile", group="projectionF2")
                    pj.hdf5file.close()
                    toreturn = 'LC-MS'
                except tables.NoSuchNodeError:
                    toreturn = '2D-MS'
            else:
                toreturn = '???'
            d.hdf5file.close()
        elif path.name == 'acqus':
            toreturn = 'FID'
        else:
            toreturn = '???'
        if DEBUG: print('**filetype** type:',toreturn)
        return toreturn
    def filetype(self, path):
        """returns filetype as a string
        filetype can be:
        FID: old style transient (Apex0)
        fid: new style transient
        ser: series of transient
        MS: Simple processed spectrum
        LC-MS: LC-MS 2D processed spectrum
        2D-MS: 2DFTMS processed spectrum
        ???: undeciferable
        """
        from tables.file import open_file
        from tables.group import Group
        from tables.leaf import Leaf
        if DEBUG: print('**filetype** path:',path, end=':')
        if path.suffix == '.d':
            if (path/'ser').exists():
                toreturn = 'ser'
            elif (path/'fid').exists():
                toreturn = 'fid'
            else:
                toreturn = '???'
        elif path.suffix == '.msh5':   # we'll read directly into the file - much faster!
            try:
                h5file = open_file(str(path), 'r')
            except:
                return '???'
            with h5file:
                nodename = '/resol1/axes'
                try:
                    nodeobject = h5file.get_node(nodename)
                except:
                    return '???'
                if isinstance(nodeobject, Leaf):
                #    print(path,nodename,'Leaf', nodeobject.shape, str(nodeobject))
                    dim = nodeobject.shape[0]
                elif isinstance(nodeobject, Group):
                    print(path,nodename,'is a Group  ???  - file ignored')
                    return '???'
                else:
                    # This should never happen
                    return '???'
                if dim == 1:
                    toreturn = 'MS'
                elif dim == 2:
                    try:
                        nodeobject = h5file.get_node('/projectionF2')
                        toreturn = 'LC-MS'
                    except tables.NoSuchNodeError:
                        toreturn = '2D-MS'
                else:
                    toreturn = '???'
        elif path.name == 'acqus':
            toreturn = 'FID'
        else:
            toreturn = '???'
        if DEBUG: print('**filetype** type:',toreturn)
        return toreturn
    @property
    def dicopath(self):
        """
        the Path(name) of the json file
        """
        return Path(self.base)/'filetypesDB.json'
    def build_dico(self):
        """
        loads the ftype dico from json file, and updates for new files
        finally store the json file again, creates it if missing
        """
        dicofile = self.dicopath
        if (dicofile).exists():
            dicodate = dicofile.stat().st_mtime
            dico = json.load(dicofile.open())
        else:
            dicodate = 0
            dico = {}
        for i in Path(self.base).glob('**/*.d'):     # Apex and Solarix
            if i.is_dir() and i.stat().st_mtime > dicodate:
                if DEBUG: print('adding', i)
                ftype = self.filetype(i)
                dico[str(i)] =  ftype 
        for i in Path(self.base).glob('**/acqus'):   # "Apex0"
            fid = i.parent/'fid'
            if (fid).exists() and fid.stat().st_mtime > dicodate:
                if DEBUG:print('adding', fid)
                ftype = self.filetype(i)
                dico[str(fid)] = ftype
        for i in Path(self.base).glob('**/*.msh5'):  # processed files
            if i.stat().st_mtime > dicodate:
                if DEBUG:print('adding', i)
                ftype = self.filetype(i)
                dico[str(i)] = ftype
        try:
            json.dump(dico, dicofile.open('w'), indent=2)
        except:
            print('*** Error while storing the filetype DB')
        return dico

    def list_from_dico(self):
        """given the computed dico of filetypes - return a list corresponding to paramters
        dotd (raw files), msh5 (processed) and accept (filtetypes)
        """
        rflist = ['   --- raw files ---']
        pflist = ['   --- processed ---']
        flist = []
        for i,ftype in self.file_dico.items():
            if ftype in self.accept:
                iP = Path(i)
                if ftype in ('fid', 'FID', 'ser') and self.dotd:
                        rflist.append(MSfile(iP, iP.relative_to(self.base), ftype)) 
                elif self.msh5 and i.endswith('.msh5'):
                        pflist.append(MSfile(iP, iP.relative_to(self.base), ftype))
        if self.dotd:
            flist = rflist
        if self.msh5:
            flist += pflist
        return  flist

    def build_list(self):
        """
        old style code - not used any more - was too slow over fuse.
        equiv to build_dico / list_from_dico
        """
        flist = []
        if self.dotd:
            flist.append('   --- raw ---')
            for i in Path(self.base).glob('**/*.d'):     # Apex and Solarix
                if i.is_dir():
                    ftype = self.filetype(i)
                    if ftype in self.accept:
                        flist.append(MSfile(i, i.relative_to(self.base), ftype)) 
            for i in Path(self.base).glob('**/acqus'):   # "Apex0"
                if (i.parent/'fid').exists():
                    ftype = self.filetype(i)
                    if ftype in self.accept:
                        flist.append(MSfile((i.parent/'fid'), i.parent.relative_to(self.base), ftype)) 
        if self.msh5:
            flist.append('   --- processed ---')
            for i in Path(self.base).glob('**/*.msh5'):
                ftype = self.filetype(i)
                if ftype in self.accept:
                    flist.append(MSfile(i, i.relative_to(self.
                    base), ftype))
        return flist

class FileChooser(VBox):
    """a simple chooser for Jupyter for selecting *.d directories
    This new version creates a list of tuple
        (fullpath, spath ftype) where 
            - fulpath is a pathlib.Path object with the path of the file
            - spath
            - ftype is a string either
                'fid' 'ser' for raw data
                'MS' 'LC-MS' or '2D-MS' for processed data
    selected is the fullpath name of the selected one
        fc = FileChooser()
        open(fc.selected)
    """
    def __init__(self, base='DATA', dotd=True, msh5=True,
                 accept=('fid', 'FID', 'ser', 'MS', 'LC-MS', '2D-MS')):
        """
        accept is a list of ftype that will added to the list
        among 'fid', 'FID', ser', 'MS', 'LC-MS', '2D-MS'
        """
        super().__init__()
        self.base = base
        self.filter = {'base':base, 'dotd':dotd, 'msh5':msh5, 'accept':accept}
        files = File_list(**self.filter)
        flist = files.list
        self.selec = widgets.Select(options=flist, rows=min(8,len(flist)), layout={'width': 'max-content'})
        self.bref = Button(description='Refresh',layout=Layout(width='10%'),
                tooltip='Refresh list')
        self.bref.on_click(self.refresh)
        first_line = HBox([widgets.HTML('<b>Choose one experiment</b>&nbsp;&nbsp;'), self.bref])
        self.children  = [first_line, self.selec ]
    def refresh(self, e):
        files = File_list(**self.filter)
        flist = files.list
        self.selec.options = files.list
        self.selec.rows = min(8,len(self.selec.options))
    @property
    def selected(self):
        if isinstance(self.selec.value, str):
            return 'None'
        else:
            return self.selec.value.fullpath
    @property
    def name(self):
        if isinstance(self.selec.value, str):
            return 'None'
        else:
            return self.selec.value.spath
class Dataproc:
    "a class to hold a 1D data set and to process it"
    def __init__(self, data):
        self.data = data    # the fid
        self.DATA = None    # the spectrum
        self.procparam = U.procparam_MS
        self.procparam["peakpicking_todo"] = "manual"
        self.procparam['zoom'] = None
        self.procparam['peakpicking_noise_level'] = 30
        self.procparam['centroid'] = "No"

    def process(self):
        if self.data.dim == 1:
            datacopy = self.data.copy()
            datacopy.fullpath = self.data.fullpath
            datacopy.filename = self.data.filename
            self.DATA = U.process_ms1d(datacopy, self.procparam)
            self.DATA.filename = self.data.filename
            self.DATA.fullpath = self.data.fullpath
            self.DATA.set_unit('m/z')
        else:
            print('Data not compatible')

    def peakpick(self):
        if self.DATA.dim == 1:
            U.peakpick_ms1d(self.DATA, self.procparam)

class IFTMS(object):
    "a widget to set all 1D MS tools into one screen"
    def __init__(self, show=True, style=True):
        # header
        #   filechooser
        self.base = BASE
        self.filechooser = FileChooser(self.base, accept=('MS','fid','FID'))
        self.datap = None
        self.MAX_DISP_PEAKS = NbMaxDisplayPeaks

        #   buttons
        #       load
        self.bload = Button(description='Load',layout=Layout(width='15%'),
                tooltip='load and display experiment')
        self.bload.on_click(self.load)
        #       FT
        self.bproc = Button(description='Process',layout=Layout(width='15%'),
                tooltip='Fourier transform of the fid')
        self.bproc.on_click(self.process)
        #       pp
        self.bpeak = Button(description='Peak Pick',layout=Layout(width='15%'),
                tooltip='Detect Peaks')
        self.bpeak.on_click(self.peakpick)
        self.bsave = Button(description='Save',layout=Layout(width='15%'),
                tooltip='Save processed data set in msh5 format')
        self.bsave.on_click(self.save)

        # GUI set-up and scene
        # tools 
        self.header = Output()
        with self.header:
            self.waitarea = Output()
            self.buttonbar = HBox([self.bload, self.bproc, self.bpeak, self.bsave, self.waitarea])
            display(Markdown('---\n# Select an experiment, and load to process'))
            display(self.filechooser)
            display(self.buttonbar)

        NODATA = HTML("<br><br><h3><i><center>No Data</center></i></h3>")
        # fid
        self.fid = Output()  # the area where 1D is shown
        with self.fid:
            display(NODATA)
            display(Markdown("use the `Load` button above"))
        # spectrum
        self.out1D = Output()  # the area where 1D is shown
        with self.out1D:
            display(NODATA)
            display(Markdown("After loading, use the `Process` or `Load` buttons above"))

        # peaklist
        self.peaklist = Output()  # the area where peak list is shown
        with self.peaklist:
            display(NODATA)
            display(Markdown("After Processing, use the `Peak Pick` button above"))

        # form
        self.outform = Output()  # the area where processing parameters are displayed
        with self.outform:
            self.paramform()
            display(self.form)

        # Info
        self.outinfo = Output()  # the area where info is shown
        self.showinfo()

        #  tabs
        self.tabs = widgets.Tab()
        self.tabs.children = [ self.fid, self.out1D, self.peaklist, self.outform, self.outinfo ]
        self.tabs.set_title(0, 'raw fid')
        self.tabs.set_title(1, 'Spectrum')
        self.tabs.set_title(2, 'Peak List')
        self.tabs.set_title(3, 'Processing Parameters')
        self.tabs.set_title(4, 'Info')

#        self.tabs = VBox([ self.out2D, self.outpp2D, self.out1D, self.outinfo ])
        self.box = VBox([   self.header,
                            self.tabs
                        ])
        # self.box = VBox([self.title,
        #                 self.FC,
        #                 HBox([self.bdisp2D, self.bpp2D, self.bdisp1D])
        #                 ])
        if style:
            injectcss()
        if show:
            display(self.box)

    def showinfo(self):
        """
        Show info on the data-set in memory - several possible cases 
        """
        self.outinfo.clear_output()
        with self.outinfo:
            if self.datap == None:
                display(HTML("<br><br><h3><i><center>No Data</center></i></h3>"))
            else:
                if self.datap.data:              #  a fid is load
                    display( Markdown("# Raw Dataset\n%s\n"%(self.selected,)) )
                    print(self.datap.data)
                    if self.datap.DATA != None:  # and has been processed
                        display( Markdown("# Audi-Trail") )
                        with open('audit_trail.txt','r') as F:
                            display(Markdown(F.read()))
                else:
                    if self.datap.DATA != None:  # a processed has been loaded
                        display( Markdown("# Processed Dataset\n%s\n"%(self.selected,)) )
                        print(self.datap.DATA)
                        with open('audit_trail.txt','r') as F:
                            display(Markdown(F.read()))
    def wait(self):
        "show a little waiting wheel"
        here = Path(__file__).parent
        with open(here/"icon-loader.gif", "rb") as F:
            with self.waitarea:
                self.wwait = widgets.Image(value=F.read(),format='gif',width=40)
                display(self.wwait)
    def done(self):
        "remove the waiting wheel"
        self.wwait.close()
    @property
    def selected(self):
        return str(self.filechooser.selected)
    @property
    def title(self):
        return str(self.filechooser.name)

    def load(self, e):
        "load 1D data-set and display"
        self.fid.clear_output(wait=True)
        if self.selected.endswith(".msh5"):
            self.loadspike()
        else:
            self.loadbruker()
    def loadspike(self):
        fullpath = self.selected
        try:
            DATA = FTICRData(name=fullpath)
        except:
            self.waitarea.clear_output(wait=True)
            with self.waitarea:
                print('Error while loading',self.selected)
                self.waitarea.clear_output(wait=True)
            with self.outinfo:
                traceback.print_exc()
            return
        data = None
        DATA.filename = self.selected      # filename and fullpath are equivalent !
        DATA.fullpath = fullpath
        audit = U.auditinitial(title="Load file", append=False)
        DATA.set_unit('m/z')
        self.datap = Dataproc(data)
        self.datap.data = None
        self.datap.DATA = DATA
        self.showinfo()
        self.out1D.clear_output()
        with self.out1D:
            DATA.display(title=self.title, new_fig={'figsize':(10,5)})
        self.tabs.selected_index = 1

    def loadbruker(self):
        fullpath = self.selected
        try:
            data = BrukerMS.Import_1D(fullpath)
        except:
            self.waitarea.clear_output(wait=True)
            with self.waitarea:
                print('Error while loading -',self.selected)
                self.waitarea.clear_output(wait=True)
            with self.outinfo:
                traceback.print_exc()
            return
        data.filename = self.selected
        data.fullpath = fullpath      # filename and fullpath are equivalent !
        audit = U.auditinitial(title="Load file", append=False)
        data.set_unit('sec')
        with self.fid:
            data.display(title=self.title,new_fig={'figsize':(10,5)})
        self.datap = Dataproc(data)
        self.showinfo()
        self.param2form(self.datap.procparam)
        self.outform.clear_output()
        with self.outform:            # refresh param form
            display(self.form)
        self.tabs.selected_index = 0

    def save(self, e):
        "save 1D spectrum to msh5 file"
        self.wait()
        audit = U.auditinitial(title="Save file", append=True)
        # find name
        try:
            fullpath = self.datap.DATA.fullpath
        except:
            self.waitarea.clear_output(wait=True)
            with self.waitarea:
                print('No processed dataset to save')
                self.waitarea.clear_output(wait=True)
            return
        # find name
        expname = U.find_free_filename(fullpath, 'Processed', '.msh5')

        # clean if required
        self.form2param()
        parameters = self.datap.procparam
        data = self.datap.DATA
        compress = False
        if parameters['grass_noise_todo'] == 'storage':           # to do !
#            print("text", "grass noise removal","noise threshold", parameters['grass_noise_level'])
            data.zeroing(parameters['grass_noise_level']*data.noise)
            data.eroding()
            compress = True
            U.audittrail( audit, "text", "grass noise removal",
                "noise threshold", parameters['grass_noise_level'])
        try:
            self.datap.DATA.save_msh5(expname, compressed=compress)
        except:
            self.waitarea.clear_output(wait=True)
            with self.waitarea:
                print('Error while saving to file',self.selected)
                self.waitarea.clear_output(wait=True)
            with self.outinfo:
                traceback.print_exc()
            return
        self.datap.DATA.filename = expname
        # copy audit_trail.txt
        pexp = Path(expname)
        destination = str(pexp.with_suffix(''))+'_audit.txt'
        subprocess.run(["mv", "audit_trail.txt", destination])

        with self.outinfo:
            display(Markdown("""# Save locally
 Data set saved as "%s"
 """%(expname,)))
        self.done()
        with self.waitarea:
            print('Data-set saved')
            self.waitarea.clear_output(wait=True)
        self.filechooser.refresh('event')

    def process(self,e):
        "do the FT"
        if self.datap == None or self.datap.data == None:
            with self.waitarea:
                print('Please load a raw dataset first')
                self.waitarea.clear_output(wait=True)
            return
        self.wait()
        self.out1D.clear_output(wait=True)
        self.form2param()
        self.datap.process()
        DATA = self.datap.DATA
        ti = self.selected
        with self.out1D:
            DATA.display(title=self.title, new_fig={'figsize':(10,5)})
        self.showinfo()
        self.tabs.selected_index = 1
        self.done()

    def peakpick(self,e):
        "do the peak-picking"
        if self.datap == None:
            with self.waitarea:
                print('Please load a dataset first')
                self.waitarea.clear_output(wait=True)
            return
        if self.datap.DATA == None:
            with self.waitarea:
                print('Please process the dataset first')
                self.waitarea.clear_output(wait=True)
            return
        self.wait()
        self.peaklist.clear_output(wait=True)
        self.form2param()
        self.datap.peakpick()
        with self.out1D:
            self.datap.DATA.display_peaks(peak_label=True ,NbMaxPeaks=self.MAX_DISP_PEAKS)
        with self.peaklist:
            display( Markdown('%d Peaks detected'%len(self.datap.DATA.peaks)) )
            display(HTML(self.datap.DATA.pk2pandas().to_html()))
        self.showinfo()
        self.tabs.selected_index = 2
        self.done()
    def paramform(self):
        "draw the processing parameter form"
        def dropdown(options,value,description):
            opt = [(v,k) for k,v in U.procparam_MS[options].items()]
            return widgets.Dropdown(options=opt, value=value, description=description, layout=ly, style=style)

        chld = []
        ly = widgets.Layout(width='50%')
        style = {'description_width': '30%'}
        chld.append(widgets.HTML('<h3>Processing</h3>'))
        
        chld.append( widgets.RadioButtons(options=['Yes','No'],value='Yes',description='center fid',layout=ly, style=style))
        
        opt = U.procparam_MS["apodisations"].keys()
        chld.append( widgets.Dropdown(options=opt,value='hamming',description='apod todo', layout=ly, style=style) )

        chld.append( widgets.IntSlider(value=2,min=1,max=4,description='zf level', layout=ly, style=style) )

        chld.append( dropdown("baseline_correction","offset","baseline todo") )

        chld.append( dropdown("grass_noise","storage","grass noise todo") )

        chld.append( widgets.FloatSlider(value=3,min=1,max=10,description='grass noise level', layout=ly, style=style) )

        chld.append(widgets.HTML('<h3>Peak Picking</h3>'))
        
        chld.append( dropdown("peakpicking","manual","peakpicking todo") )
        
        chld.append( widgets.FloatLogSlider(value=10,min=0,max=3,description='peakpicking noise level', layout=ly, style=style) )

        chld.append( widgets.RadioButtons(options=['Yes','No'],value='Yes',description='centroid',layout=ly, style=style))

        chld.append( widgets.IntText(value=self.MAX_DISP_PEAKS,min=10,max=10000,description='max peak displayed', layout=ly, style=style) )


        self.form = widgets.VBox(chld)

    # WARNING procparams have '_' in names while the form display with ' '
    def param2form(self, dico, verbose=DEBUG):
        """copy parameters stored in dico to form."""
        myform = {}                       # a dico to handle widgets in the form
        for vb in self.form.children:
            myform[vb.description] = vb
        keys = myform.keys()              # keys of form
        # then propagate
        for k,v in dico.items():
            k = k.replace('_',' ')
            if k not in keys:
                if verbose:
                    print ('key not in form:',k)
            else:
                myform[k].value = v

    def form2param(self, verbose=DEBUG):
        """copy form parameters to internal parameters."""
        val = self.form2dico()
        keys = self.datap.procparam.keys()   # keys of the procparam
        for k,v in val.items():
            if k not in keys:
                if k == 'max_peak_displayed':
                    self.MAX_DISP_PEAKS = v
                elif verbose:
                    print ('key missmatch:',k)
                continue
            self.datap.procparam[k] = v

    def form2dico(self):
        """copy form parameters to a dico."""
        val = {}
        for vb in self.form.children:
            k = vb.description.replace(' ','_')
            val[k] = vb.value
        return val


class Calib(object):
    "a simple tool to show and modify calibration cste"
    def __init__(self, data):
        self.data = data
        self.res = [data.axis1.calibA, data.axis1.calibB, data.axis1.calibC]
        self.A = widgets.FloatText(value=data.axis1.calibA, description="A")
        self.B = widgets.FloatText(value=data.axis1.calibB, description="B")
        self.C = widgets.FloatText(value=data.axis1.calibC, description="C")
        self.bupdate = widgets.Button(description="Update",
                tooltip='set current data-sets to displayed values')
        self.bupdate.on_click(self.update)
        self.bback = widgets.Button(description="Restore",
                tooltip='restore dataset to initial values')
        self.bback.on_click(self.back)
        display(VBox([  HBox([self.A, widgets.Label('Hz/Th')]),
                        HBox([self.B, widgets.Label('Hz')]),
                        HBox([self.C, widgets.Label('Hz/Th^2')]),
                        HBox([self.bupdate, self.bback])]))
    def update(self,event):
        self.data.axis1.calibA = self.A.value
        self.data.axis1.calibB = self.B.value
        self.data.axis1.calibC = self.C.value
        print("Set - don't forget to rerun the Peak Picker")
    def back(self,event):
        self.data.axis1.calibA = self.res[0]
        self.data.axis1.calibB = self.res[1]
        self.data.axis1.calibC = self.res[2]
        self.A.value = self.res[0]
        self.B.value = self.res[1]
        self.C.value = self.res[2]

Colors = ('black','red','blue','green','orange',
'blueviolet','crimson','turquoise','indigo',
'magenta','gold','pink','purple','salmon','darkblue','sienna')

class SpforSuper(object):
    "a holder for SuperImpose"
    def __init__(self, i, name):
        j = i%len(Colors)
        self.name = widgets.Text(value=name, layout=Layout(width='70%'))
        self.color = widgets.Dropdown(options=Colors,value=Colors[j],layout=Layout(width='10%'))
        self.direct = widgets.Dropdown(options=['up','down','off'],value='off', layout=Layout(width='10%'))
        self.me = HBox([widgets.HTML(value="<b>%d</b>"%i),self.name, self.color,self.direct])
        self.fig = False
    def display(self):
        if self.name != 'None' and self.direct.value != 'off':
            scale = 1
            if self.direct.value == 'up':
                mult = 1
            elif self.direct.value == 'down':
                mult = -1
            else:
                return
            FTICRData(name=self.name.value).set_unit('m/z').mult(mult).display(
                new_fig=self.fig,
                scale=scale,
                color=self.color.value,
                label=op.basename(op.dirname(self.name.value)))

class SuperImpose(object):
    "a tool to superimpose spectra"
    def __init__(self, base=None, ftype='*.msh5', N=None):
        if N is None:
            N = int(input('how many spectra do you want to compare:  '))
        self.Chooser = FileChooser(base=base, ftype=ftype, mode='r', show=False)
        self.bsel = widgets.Button(description='Copy',layout=Layout(width='10%'),
                tooltip='copy selected data-set to entry below')
        self.to = widgets.IntText(value=1,min=1,max=N,layout=Layout(width='10%'))
        self.bsel.on_click(self.copy)
        self.bdisplay = widgets.Button(description='Display',layout=Layout(width='10%'),
                button_style='info', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='display superimposition')
        self.bdisplay.on_click(self.display)
        self.spec = Output(layout={'border': '1px solid black'})
        self.DataList = [SpforSuper(i+1,'None') for i in range(N)]
        self.DataList[0].color.value = 'black'
        self.DataList[0].fig = True  # switches on the very first one
    def Show(self):
        display(widgets.Label('Select a file, and click on the Copy button to copy it to the chosen slot'))
        self.Chooser.show()
        display(HBox([self.bsel, widgets.Label('to'), self.to]))
        display(VBox([sp.me for sp in self.DataList]))
        display(self.bdisplay)
        display(self.spec)
    def copy(self, event):
        if self.to.value <1 or self.to.value >len(self.DataList):
            print('Destination is out of range !')
        else:
            self.DataList[self.to.value-1].name.value = self.Chooser.file
            self.DataList[self.to.value-1].direct.value = 'up'
        self.to.value = min(self.to.value, len(self.DataList)) +1
    def display(self, event):
        self.spec.clear_output(wait=True)
        for i,s in enumerate(self.DataList):
            with self.spec:
                s.display()

