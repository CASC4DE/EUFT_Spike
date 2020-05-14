#!/usr/bin/env python 
# encoding: utf-8

"""
A tool to display LC FT-ICR data-sets

to be embedded in jupyter notebook

CB / MAD Jan 2020

This version requires ipympl (see: https://github.com/matplotlib/jupyter-matplotlib )
and the notebook to be opened with %matplotlib widget
"""
import os.path as op
from pathlib import Path
import time
import tables
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from ipywidgets import interact, fixed, HBox, VBox, GridBox, Label, Layout, Output, Button
import ipywidgets as widgets
from IPython.display import display, Markdown, HTML, Image, clear_output
import numpy as np
from xml.etree import cElementTree as ET

from spike import FTICR
from spike.NPKData import flatten, parsezoom, TimeAxis
from spike.Interactive.ipyfilechooser import FileChooser
from spike.FTMS import FTMSData
from spike.FTICR import FTICRData
from spike.File.HDF5File import HDF5File
from . import FTICR_INTER as FI

# REACTIVE modify callback behaviour
# True is good for inline mode / False is better for notebook mode
REACTIVE = True
HEAVY = False
DEBUG = False

BASE = 'FTICR_DATA'              # name of the 
SIZEMAX = 8*1024*1024        # largest zone to display
NbMaxDisplayPeaks = 200      # maximum number of peaks to display at once

def Set_Table_Param():
#    if debug>0: return
    tables.parameters.CHUNK_CACHE_PREEMPT = 1
    tables.parameters.CHUNK_CACHE_SIZE = 100*1024*1024
    tables.parameters.METADATA_CACHE_SIZE  = 100*1024*1024
    tables.parameters.NODE_CACHE_SLOTS = 100*1024*1024
    #tables.parameters.EXPECTED_ROWS_EARRAY = 100
    #tables.parameters.EXPECTED_ROWS_TABLE =100
    #tables.parameters.MAX_THREADS = 8
    #tables.parameters.PYTABLES_SYS_ATTRS = False

# TOOLS FOR LC FTICR
class MR(object):
    "this class handles multiresolution datasets"
    def __init__(self, name, report=True, Debug=DEBUG):
        "name : filename of the msh5 multiresolution file"
        Set_Table_Param()
        self.SIZEMAX = SIZEMAX
        self.name = name
        self.data = []                   # will contain all resolutions
        self.min, self.tic, self.mxpk = self.readScanXML()
        self.load()
        self.compute_absmax()
        self.axis1 = self.data[0].axis1
        self.axis2 = self.data[0].axis2
#        self.col0 = self.data[0].col
#        self.row0 = self.data[0].row
        self.highmass = self.data[0].axis2.highmass     # a tuple (h1, h2)
        self.Tmin = float(self.data[0].axis1.Tmin/60)   # internal is in sec - display is in min.
        self.Tmax = float(self.data[0].axis1.Tmax/60)
        self.Debug = Debug
        if report: self.report()

    def readScanXML(self):
        "read associated xml file and returns minutes, tic and max peak list"
        hdf = HDF5File(fname=self.name)
        data = hdf.open_internal_file('scan.xml').read()
        res = ET.fromstring(data)
        tic_list = []
        minutes_list = []
        maxpeak_list = []
        for word in res:
            tic = float(word.find('tic').text)
            tic_list.append(tic)
            minutes = float(word.find('minutes').text)
            minutes_list.append(minutes)
            maxpeak = float(word.find('maxpeak').text)
            maxpeak_list.append(maxpeak)
        return (minutes_list, tic_list, maxpeak_list)

    def load(self):
        "load from file"
        # load all resolution
        self.data = []
        for i in range(8):
            try:
                dl = FTICR.FTICRData(name=self.name, mode="onfile", group="resol%d"%(i+1))
            except tables.NoSuchNodeError:
                pass
            else:
                self.data.append(dl)
                self.title = op.basename(self.name)
        # set-up details
        for d in self.data:
            if d.size1 != len(self.min):
                step = len(self.min)//d.size1
                tval = self.min[::step]
            else:
                tval = self.min
            d.axis1 = TimeAxis(size=d.size1, tabval=tval, importunit="min", currentunit='sec' )
            d.axis1.currentunit='min'
            d.axis2.currentunit='m/z'
        # load projection
        try:
            pj = FTICR.FTICRData(name=self.name, mode="onfile", group="projectionF2")
        except tables.NoSuchNodeError:
            for d in self.data:
                if d.size2 < 100000:
                    p = d.get_buffer()[:,:]
                    pj = d.row(0)
                    pj.set_buffer(p.max(0))   # is small enough compute a projection
        pj.axis1 = self.data[0].axis2
        pj.set_unit('m/z')
        self.proj2 = pj

    def report(self):
        "report object content"
        print (self.name)
        print(self.data[0])
        print('=====================')
        print('LC-MS multiresolution data:\n#: Size')
        for i,dl in enumerate(self.data):
            print ("%d: %d x %d : %.0f Mpix"%( i+1, dl.size1, dl.size2, dl.size1*dl.size2/1024/1024 ))
    def _report(self):
        "low level report"
        for i,dl in enumerate(self.data):
            print(i+1)
            print(dl)
    def colmz(self,i):
        "return a column with coordinate in m/z"
        return self.col(self.axis2.mztoi(i))
    def rowmz(self,i):
        "return a row with coordinate in m/z"
        return self.row(self.axis1.mztoi(i))
    def col(self,i):
        "return a column with coordinate in index"
        return self.col(int(round(i)))
    def row(self,i):
        "return a row with coordinate in index"
        return self.row(int(round(i)))
    def to_display(self,zoom=((0,1),(0,FTICR.FTMS.HighestMass)), verbose=False):
        """
        computes and return which dataset to display at a given zoom and scale level"
        in: zoom = ((tlow, tup), (F2low,F2up))  - in min / m/z

        out: a tuple (data, zoomwindow), where data is a NPKData and zoomwindow an eventually recalibrated zoom window

        so, if DATA is an MR() object and Zoom a defined window in m/z ((F1low, F1up), (F2low,F2up))
        the sequence:
            datasel, zz = DATA.to_display(Zoom)
            datasel.display(zoom=zz, scale=...)
        will display the selected zone with the best possible resolution
        """
        # WARNING - different from 2DFTICR version
        z1,z2,z3,z4 = flatten(zoom)
        if verbose: print ("F1: %.1f - %.1f  min / F2: %.1f - %.1f m/z"%(z1,z2,z3,z4))
        z1,z2 = min(z1,z2), max(z1,z2)
        z3,z4 = min(z3,z4), max(z3,z4)
        for reso,dl in enumerate(self.data):
            z11 = max(z1, self.Tmin)
            z33 = max(z3, float(dl.axis2.lowmass))
            z22 = min(z2, self.Tmax)
            z44 = min(z4, self.highmass)
            z1lo, z1up, z2lo, z2up = parsezoom(dl,(z11,z22,z33,z44))
            sz = (z1lo-z1up)* (z2lo-z2up)
            if sz < self.SIZEMAX:
                if verbose: print (reso, dl.size1,dl.size2, z1lo, z1up, z2lo, z2up, sz)
                break
        zooml = (dl.axis1.itom(z1lo), dl.axis1.itom(z1up), dl.axis2.itomz(z2up), dl.axis2.itomz(z2lo))
        if verbose or self.Debug:
            print ("zoom: F1 %.1f-%.1f  /  F2 %.1f-%.1f"%zooml)
            print ("resolution level %d - %.1f Mpix zoom window"%(reso, sz/1024/1024))
        return dl, zooml
    def compute_absmax(self):
        "computes largest point from smaller resolution, and propagates"

        hf = self.data[0]
        try:
            maxvalues = hf.hdf5file.retrieve_object('maxvalues')
        except:
            maxvalues = None 
        if maxvalues is None:
            dsmall = self.data[-1]
            self.absmax = dsmall.absmax
            a = dsmall.absmax
            for dl in self.data[::-1]:
                dl._absmax = a
                a *= 4
        else:
            for i, m in enumerate(maxvalues):
                self.data[i]._absmax = m

def different(a,b):
    "True if more than x% different"
    return abs( 2*(a-b)/(a+b)) > 0.05
class MR_interact(MR):
    def __init__(self, name, figsize=(15,6), report=True, show=True, Debug=DEBUG):
        """
        creates an interactive object.
        if display is True (default) the graphical tool will be displayed.
        """
        super(MR_interact, self).__init__(name, report=report, Debug=Debug)
        self.vlayout = Layout(width='60px')
        self.spec_ax = None
        self.figsize = figsize
#        self.reset_track()
        self.log = []
        if show:  self.show()

    def bb(self, name, desc, action, layout=None, tooltip=""):
        "build a button into self"
        if layout is None: layout = self.vlayout
        butt = widgets.Button(description=desc, layout=layout, tooltip=tooltip)
        butt.on_click(action)
        setattr(self, name, butt)

    def check_fig(self):
        "create figure if missing"
        if self.spec_ax is None:
            grid = {'height_ratios':[1,4],'hspace':0,'wspace':0}
            grid['width_ratios']=[7,1]
    #        fig, self.axarr = plt.subplots(2, 1, sharex=True, figsize=fsize, gridspec_kw=grid)
            plt.ioff()
            self.fig = plt.figure(figsize=self.figsize, constrained_layout=False)
            spec2 = gridspec.GridSpec(ncols=2, nrows=2, figure=self.fig, **grid)
            axarr = np.empty((2,2), dtype=object)
            axarr[0,0] = self.fig.add_subplot(spec2[0, 0])
            axarr[1,0] = self.fig.add_subplot(spec2[1, 0],sharex=axarr[0, 0])
            axarr[1,1] = self.fig.add_subplot(spec2[1, 1],sharey=axarr[1, 0])
            self.top_ax = axarr[0,0]
            self.spec_ax = axarr[1,0]
            self.side_ax = axarr[1,1]
            self.box = self.zoom_box()
            self.sbox = self.spec_box()
            self.set_on_redraw()
            plt.ion()

    def zoom_box(self):
        "defines the zoom box widget"
        # .  F1 .
        # F2 .  F2
        # .  F1 .
        wf = widgets.BoundedFloatText
        ref = self.data[0]
        style = {'description_width': 'initial'}
        lay = Layout(width='100px', height='30px')
        self.z1l = wf(  min=self.Tmin, max=self.Tmax,
            tooltip='vertical zoom', style=style, layout=lay)
        self.z1h = wf(  min=self.Tmin, max=self.Tmax,
            style=style, layout=lay)
        self.z2l = wf(  min=ref.axis2.lowmass, max=self.highmass,
            style=style, layout=lay)
        self.z2h = wf(  min=ref.axis2.lowmass, max=self.highmass,
            style=style, layout=lay)
        self.fullzoom()
        self.bb('b_zupdate', 'Apply', lambda e : self.display(),
            layout=Layout(width='100px'), tooltip="Set zoom to values")
        self.bb('b_reset', 'Reset', self.reset,
            layout=Layout(width='100px'), tooltip="Set zoom to values")
        blank = widgets.HTML("&nbsp;",layout=lay)
        label =  widgets.HTML('Zoom Window (in <i>m/z</i>)')
        innerbox = VBox([ label,
                    HBox([blank,    self.z1h, blank]),  
                    HBox([self.z2l, self.b_zupdate,    self.z2h]),
                    HBox([blank,    self.z1l, blank]),  
                ]
            )
#        action_box = VBox([blank ])
#        box = HBox([ self.b_reset, innerbox])
        return innerbox
    def spec_box(self):
        "defines the spectral box widget"
        self.scale = widgets.FloatLogSlider(description='scale:', value=1.0, min=-1, max=3, step=0.1,
                    tooltip='Set display scale', layout=Layout(height='400px'), continuous_update=HEAVY,
                    orientation='vertical')
        self.scale.observe(self.ob)
        self.bb('b_redraw', 'Redraw', lambda e : self.display(),
            layout=Layout(width='100px'))
        box = VBox([self.b_reset, self.scale, self.b_redraw], layout=Layout(min_width='105px'))
        return HBox([box, self.fig.canvas])
    # def scale_up(self, step):
    #     self.scale.value *= 1.1892**step # 1.1892 is 4th root of 2.0
    def show(self):
        "actually show the graphical tool and the interactive spectrum"
        self.check_fig()
        display(self.box)
        display(self.sbox)
        self.display(new=True)
    def ob(self, event):
        "observe events and display"
        if event['name'] != 'value':
            return
        self.display()
    def display(self, new=False):
        "computes pictures (display in the SPIKE sense - not ipywidget one)"
        zoom = (self.z1l.value, self.z1h.value, self.z2l.value, self.z2h.value)
        datasel, zz = self.to_display(zoom)
        corner = zz[2]
        reso = corner/datasel.axis2.deltamz(corner)
#        print(corner, reso)
        self.check_fig()  # insure figure is there
#        with self.out:
        if new:
            self.top_ax.clear() # clear
            self.proj2.display(figure=self.top_ax, title=self.title)
            self.side_ax.clear() # clear
            self.side_ax.plot(self.tic, self.min)
            self.side_ax.set_title('TIC')
        self.spec_ax.clear() # clear 
        datasel.display(zoom=zz, scale=self.scale.value, 
            xlabel='m/z', ylabel='time '+self.data[0].axis1.currentunit,
            show=False, figure=self.spec_ax)
        self.spec_ax.text(corner,zz[1], "D#%d R: %.0f"%(self.data.index(datasel)+1, reso))
        self.side_ax.set_ybound(zz[0], zz[1])   # for some strange reason (mpl 3.1.0 bug ?), this is needed...
        self.top_ax.set_xbound(zz[2], zz[3])
        if self.Debug:
            xb = self.top_ax.get_xbound()
            yb = self.side_ax.get_ybound()
            self.log.append(('display',zz, yb, xb))

    def update(self, e):
        "update internal zoom coordinates"
#        self.track.append((self._zoom, self.scale))
#        self.point = -1 # means last
        xb = self.spec_ax.get_xbound()
        yb = self.spec_ax.get_ybound()
        diff =  different(self.z1l.value, yb[0]) or \
                different(self.z1h.value, yb[1]) or \
                different(self.z2l.value, xb[0]) or \
                different(self.z2h.value, xb[1])
        if diff:
            self.z1l.value = yb[0]
            self.z1h.value = yb[1]
            self.z2l.value = xb[0]
            self.z2h.value = xb[1]
            self.log.append(('update - ', yb, xb))
            self.display()
        else:
            if self.Debug:
                self.log.append('update - no action')
#            time.sleep(0.2)
    def set_on_redraw(self):
        def on_press(event):
            print('you pressed', event.button, event.xdata, event.ydata)
        def on_release(event):
            print('you released', event.button, event.xdata, event.ydata)
        # def on_scroll(event):
        #     self.scale_up(event.step)
        cidd = self.fig.canvas.mpl_connect('draw_event', self.update)
#        cids = self.fig.canvas.mpl_connect('scroll_event', on_scroll)
#        cidp = self.fig.canvas.mpl_connect('button_press_event', on_press)
#        cidr = self.fig.canvas.mpl_connect('button_release_event', on_release)
        pass
    def reset(self, b):
        self.scale.value = 1.0
        self.fullzoom()
        self.display()
    def fullzoom(self):
        self.z1l.value = self.Tmin
        self.z1h.value = self.Tmax
        self.z2l.value = self.axis2.lowmass+0.01
        self.z2h.value = self.highmass

class LC1D(VBox):
    """
    Define a tool to explore slices extracted from a LC-MS experiment
    """
    def __init__(self, MRdata=None, show=True, Debug=DEBUG):
        "MRData should be a MR() object"
        super(LC1D, self).__init__()
        # initialize data
        self.MR = MRdata
        self.data = MRdata.data[0]
        self.sizeLC = self.data.size1
        self.sizeMS = self.data.size2
        self.debug = Debug
        # templates
        self.LC = self.data.col(0)
        self.MS = self.data.row(0)
        # current ones
        self.lc = None
        self.ms = None

        # then graphic
        self.fig = None
        self.ax = None
        plt.ioff()
        self.fig, self.ax = plt.subplots(figsize=(15,3))
        plt.ion()
        self.box = self.buildbox()
        if show:
            self.show()
    def wait(self):
        "show a little waiting wheel"
        here = Path(__file__).parent
        with open(here/"icon-loader.gif", "rb") as F:
            self.wwait = widgets.Image(value=F.read(),format='gif',width=40)
            display(self.wwait)
    def done(self):
        "remove the waiting wheel"
        self.wwait.close()

    def bb(self, name, desc, action, layout, tooltip=""):
        "build a button into self"
        butt = widgets.Button(description=desc, layout=layout, tooltip=tooltip)
        butt.on_click(action)
        setattr(self, name, butt)
    def buildbox(self):
        "builds the actions box"
        dstyle = {'description_width': 'initial'}
        # LC
        self.bb('bMS', 'get', self.computeMS,
            layout=Layout(flex='0.5',width='60px'))
        LCstep = self.LC.axis1.itom(1) - self.LC.axis1.itom(0)
        self.LCpos = widgets.FloatSlider(value=0.1, step=LCstep, min=self.LC.axis1.Tmin/60, max=self.LC.axis1.Tmax/60,
            description='min.',style=dstyle, readout=False,
            layout=Layout(flex='4'))

        self.lcread = widgets.FloatText(value=0.1, step=LCstep, min=self.LC.axis1.Tmin/60, max=self.LC.axis1.Tmax/60,
            layout=Layout(width='7em'))
        def on_lcread(e):
            self.LCpos.value = self.lcread.value
        def on_lcpos(e):
            self.lcread.value = self.LCpos.value
        self.lcread.observe(on_lcread)
        self.LCpos.observe(on_lcpos)

        self.LCspread = widgets.FloatSlider(min=LCstep, max=5.0, step=LCstep,
            description='±', style=dstyle,
            layout=Layout(flex='3'))
        # MS
        self.bb('bLC', 'get', self.computeLC,
            layout=Layout(flex='0.5',width='60px'))
        self.MSpos = widgets.FloatSlider(value=200.0, step=0.01,
            min=self.MS.axis1.lowmass, max=self.MS.axis1.highmass,
            description='m/z', style=dstyle, readout=False,
            layout=Layout(flex='4'))
        self.msread = widgets.FloatText(value=200.0, step=0.01,
            min=self.MS.axis1.lowmass, max=self.MS.axis1.highmass,
            layout=Layout(width='7em'))
        def on_msread(e):
            self.MSpos.value = self.msread.value
        def on_mspos(e):
            self.msread.value = self.MSpos.value
        self.msread.observe(on_msread)
        self.MSpos.observe(on_mspos)
        self.MSspread = widgets.FloatLogSlider(value=0.01, min=-3, max=0,
            description='±',style=dstyle, disabled = False,
            layout=Layout(flex='3'))

#        self.smooth = widgets.Dropdown(options=['Yes','No'],value='No',
#            description='smoothing:',
#            layout=Layout(flex='1'))
        self.SMstrength = widgets.IntSlider(description='smoothing:',value=5, min=0, max=10,disabled=False,
            continuous_update=HEAVY, layout=Layout(flex='2'))
        # def on_sm_change(e):
        #     if self.smooth.value == 'No':
        #         self.SMstrength.disabled = True
        #     else:
        #         self.SMstrength.disabled = False
        #     self.displayLC()
#        self.smooth.observe(on_sm_change)
        def on_smst_change(e):
            self.displayLC()
        self.SMstrength.observe(on_smst_change)

        info1 = widgets.HTML('<center>Action</center>', layout=Layout(flex='0.5'))
        info2 = widgets.HTML('<center>Coordinates</center>', layout=Layout(flex='4'))
        info3 = widgets.HTML('<center>Take mean over</center>', layout=Layout(flex='3'))
        info4 = widgets.HTML('<center>Smoothing the chromatogram</center>', layout=Layout(flex='2'))
        space1 = widgets.HTML('&nbsp;', layout=Layout(flex='2'))
        labellc = widgets.HTML('<center><b>LC dimension</b></center>',layout=Layout(flex='1', text_align='right'))
        labelms = widgets.HTML('<center><b>MS dimension</b></center>',layout=Layout(flex='1'))
        # return VBox([   HBox([info1, info2, info3, info4],
        #                         layout=Layout(justify_content="space-around")),
        #                 HBox([self.bMS, self.LCpos, self.LCspread],layout=Layout(width='70%')),
        #                 HBox([self.bLC, self.MSpos, self.MSspread,self.smooth, self.SMstrength]),
        #                 self.fig.canvas],
        #             layout=Layout(width='100%',border='solid 2px',))
        return VBox([   HBox([info2, info3, info4, info1],
                                layout=Layout(justify_content="space-around")),
                        HBox([labelms, self.lcread, self.LCpos, self.LCspread, space1, self.bMS]),
                        HBox([labellc, self.msread, self.MSpos, self.MSspread, self.SMstrength,self.bLC]),
                        self.fig.canvas],
                    layout=Layout(width='100%',border='solid 2px',))

    def computeLC(self,e):
        "compute LC profile from values"
        self.wait()
        start = self.MSpos.value - self.MSspread.value/2
        end = self.MSpos.value + self.MSspread.value/2
        istart = int( self.MS.axis1.mztoi( end ) )
        iend =  int( self.MS.axis1.mztoi( start ) )
        lc = self.data.col(istart)
        if iend>istart:
            for i in range(istart+1,iend+1):
                lc += self.data.col(i)
            lc.mult(1/(iend-istart))  # take the mean
        lc.title = "Chrom. Profile extracted from %.4f to %.4f m/z"%(start,end)
        self.lc = lc
        self.displayLC()
        self.done()

    def computeMS(self,e):
        "compute MS profile from values"
        self.wait()
        start = self.LCpos.value - self.LCspread.value/2
        end = self.LCpos.value + self.LCspread.value/2
        istart = int( self.LC.axis1.mtoi( end ) )
        iend =  int( self.LC.axis1.mtoi( start ) )
        ms = self.data.row(istart)
        if iend>istart:
            for i in range(istart+1,iend+1):
                ms += self.data.row(i)
            ms.mult(1/(iend-istart))  # take the mean
        ms.title = "MS Spectrum extracted from %.2f to %.2f minute"%(start,end)
        self.ms = ms
        self.displayMS()
        self.done()

    def show(self):
        "display the graphic widget"
        display(self.box)
        self.displayLC()
#        display(HTML('<p> </p>'))

    def displayLC(self):
        "draws the LC data"   
        try:
            d = self.lc.copy()
        except:
            d = None
        self.ax.clear()
        if d is not None:
            if self.SMstrength.value>0: #self.smooth.value == 'Yes':
                d.eroding().sg(21,11-self.SMstrength.value).plus()
            d.display(figure=self.ax, title=self.lc.title)
        else:
            display(HTML("<br><br><h3><i><center>No Data</center></i></h3>"))

    def displayMS(self):
        "draws the LC data"   
        try:
            d = self.ms.copy()
        except:
            d = None
        self.ax.clear()
        if d is not None:
            d.display(figure=self.ax, title=self.ms.title)
        else:
            display(HTML("<br><br><h3><i><center>No Data</center></i></h3>"))

    def _display(self,mode='LC'):
        "draws the data"   
        if mode == 'LC':
            try:
                d = self.lc.copy()
            except:
                d = None
        if mode == 'MS':
            try:
                d = self.ms.copy()
            except:
                d = None
        self.ax.clear()
        if d is not None:
            if mode == 'LC' and self.smooth.value == 'Yes':
                d.eroding().sg(21,11-self.SMstrength.value).plus()
            d.display(figure=self.ax)
        else:
            display(HTML("<br><br><h3><i><center>No Data</center></i></h3>"))

class MSPeaker(object):
    "a peak-picker for MS experiments"
    def __init__(self, npkd, pkname):
        if not isinstance(npkd, FTMSData):
            raise Exception('This modules requires a FTMS Dataset')
        self.npkd = npkd
        self.pkname = pkname
        self.zoom = widgets.FloatRangeSlider(value=[npkd.axis1.lowmass, npkd.axis1.highmass],
            min=npkd.axis1.lowmass, max=npkd.axis1.highmass, step=0.1,
            layout=Layout(width='100%'), description='zoom',
            continuous_update=False, readout=True, readout_format='.1f',)
        self.zoom.observe(self.display)
        self.tlabel = Label('threshold (x noise level):')
        self.thresh = widgets.FloatLogSlider(value=20.0,
            min=np.log10(1), max=2.0, base=10, step=0.01, layout=Layout(width='30%'),
            continuous_update=False, readout=True, readout_format='.1f')
        self.thresh.observe(self.pickpeak)
        self.peak_mode = widgets.Dropdown(options=['marker', 'bar'],value='marker',description='show as')
        self.peak_mode.observe(self.display)
        self.bexport = widgets.Button(description="Export",layout=Layout(width='7%'),
                button_style='success', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Export to csv file')
        self.bexport.on_click(self.pkexport)
        self.bprint = widgets.Button(description="Print", layout=Layout(width='7%'),
                button_style='success', tooltip='Print to screen')
        self.bprint.on_click(self.pkprint)
        self.bdone = widgets.Button(description="Done", layout=Layout(width='7%'),
                button_style='warning', tooltip='Fix results')
        self.bdone.on_click(self.done)
        #self.spec = Output(layout={'border': '1px solid black'})
        self.out = Output(layout={'border': '1px solid red'})
        display( VBox([self.zoom,
                      HBox([self.tlabel, self.thresh, self.peak_mode, self.bprint, self.bexport, self.bdone])
                      ]) )
        self.fig, self.ax = plt.subplots()
        self.npkd.set_unit('m/z').peakpick(autothresh=self.thresh.value, verbose=False, zoom=self.zoom.value).centroid()
        self.display()
        display(self.out)

    def pkprint(self,event):
        self.out.clear_output(wait=True)
        with self.out:
            display(HTML(self.npkd.pk2pandas().to_html()))
            #print(self.pklist())
    def pkexport(self,event):
        "exports the peaklist to file"
        with open(self.pkname,'w') as FPK:
            print(self.pklist(),file=FPK)
        print('Peak list stored in ',self.pkname)
    def pklist(self):
        "creates peaklist"
        text = ["m/z\t\tInt.(%)\tR\tarea(a.u.)"]
        data = self.npkd
        intmax = max(data.peaks.intens)/100
        for pk in data.peaks:
            mz = data.axis1.itomz(pk.pos)
            Dm = 0.5*(data.axis1.itomz(pk.pos-pk.width) - data.axis1.itomz(pk.pos+pk.width))
            area = pk.intens*Dm
            l = "%.6f\t%.1f\t%.0f\t%.0f"%(mz, pk.intens/intmax, round(mz/Dm,-3), area)
            text.append(l)
        return "\n".join(text)
    def display(self, event={'name':'value'}):
        "display spectrum and peaks"
        if event['name']=='value':  # event is passed by GUI - make it optionnal
            self.ax.clear()
            self.npkd.display(new_fig=False, figure=self.ax, zoom=self.zoom.value)
            try:
                self.npkd.display_peaks(peak_label=True, peak_mode=self.peak_mode.value, figure=self.ax, zoom=self.zoom.value, NbMaxPeaks=NbMaxDisplayPeaks)
                x = self.zoom.value
                y = [self.npkd.peaks.threshold]*2
                self.ax.plot(x,y,':r')
                self.ax.annotate('%d peaks detected'%len(self.npkd.peaks) ,(0.05,0.95), xycoords='figure fraction')
            except:
                pass
    def pickpeak(self, event):
        "interactive wrapper to peakpick"
        if event['name']=='value':
            self.pp()
    def pp(self):
        "do the peak-picking calling pp().centroid()"
        #self.spec.clear_output(wait=True)
        self.npkd.set_unit('m/z').peakpick(autothresh=self.thresh.value, verbose=False, zoom=self.zoom.value).centroid()
        self.display()
    def done(self, event):
        "exit GUI"
        for w in [self.zoom, self.thresh, self.peak_mode, self.bprint, self.bexport, self.bdone]:
            w.close()
        self.tlabel.value = "threshold %.2f noise level"%self.thresh.value
#        self.display()

class Calib(object):
    "a simple tool to show and modify calibration cste"
    def __init__(self, data):
        self.data = data
        self.res = [data.axis1.calibA, data.axis1.calibB, data.axis1.calibC]
        self.A = widgets.FloatText(value=data.axis1.calibA, description="A")
        self.B = widgets.FloatText(value=data.axis1.calibB, description="B")
        self.C = widgets.FloatText(value=data.axis1.calibC, description="C")
        self.bupdate = widgets.Button(description="Update",
                button_style='success', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='set current data-sets to displayed values')
        self.bupdate.on_click(self.update)
        self.bback = widgets.Button(description="Restore",
                button_style='success', # 'success', 'info', 'warning', 'danger' or ''
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
    def __init__(self, base=None, filetype='*.msh5', N=None):
        if N is None:
            N = int(input('how many spectra do you want to compare:  '))
        self.Chooser = FileChooser(base=base, filetype=filetype, mode='r', show=False)
        self.bsel = widgets.Button(description='Copy',layout=Layout(width='10%'),
                button_style='info', # 'success', 'info', 'warning', 'danger' or ''
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

class MS2Dscene(object):
    "a widget to set all MS tools into one screen"
    def __init__(self, show=True, style=True, Debug=DEBUG):
        # header
        #   filechooser
        self.base = BASE
        self.filechooser = FI.FileChooser(self.base, dotd=False)
        self.datap = None
        self.MAX_DISP_PEAKS = NbMaxDisplayPeaks
        self.debug = Debug

        #   buttons
        #       load
        self.bload = Button(description='Load',  #layout=Layout(width='15%'),
                tooltip='load and display experiment')
        self.bload.on_click(self.load2D)
        #       pp
        self.bpeak = Button(description='Peak Pick', #layout=Layout(width='15%'),
                 tooltip='Detect Peaks')
#        self.bpeak.on_click(self.peakpick)

        # GUI set-up and scene
        # tools 
        self.header = Output()
        with self.header:
            self.waitarea = Output()
            self.buttonbar = HBox([self.bload, self.bpeak, self.waitarea])
            display(Markdown('---\n# Select an experiment, and load'))
            display(self.filechooser)
            display(self.buttonbar)

        NODATA = HTML("<br><br><h3><i><center>No Data</center></i></h3>")
        # 2D spectrum
        self.out2D = Output()  # the area where 2D is shown
        with self.out2D:
            display(NODATA)
            display(Markdown("use the `Load` button above"))
        # 1D spectrum
        self.out1D = Output()  # the area where 1D is shown
        with self.out1D:
            display(NODATA)
            display(Markdown("After loading, this window will be activated"))

        # peaklist
        self.peaklist = Output()  # the area where peak list is shown
        with self.peaklist:
            display(HTML("<br><br><h3><i><center>This part is still in development</center></i></h3>"))

        # # form
        # self.outform = Output()  # the area where processing parameters are displayed
        # with self.outform:
        #     self.paramform()
        #     display(self.form)

        # Info
        self.outinfo = Output()  # the area where info is shown
        with self.outinfo:
            display(NODATA)

        self.out2D.clear_output(wait=True)
        self.out1D.clear_output(wait=True)
        self.outinfo.clear_output(wait=True)
        self.peaklist.clear_output(wait=True)

        #  tabs
        self.tabs = widgets.Tab()
        self.tabs.children = [ self.out1D, self.out2D, self.peaklist, self.outinfo ]
        self.tabs.set_title(0, '1D Extraction')
        self.tabs.set_title(1, '2D Display')
        self.tabs.set_title(2, 'Peak List')
        # self.tabs.set_title(3, 'Processing Parameters')
        self.tabs.set_title(3, 'Info')

#        self.tabs = VBox([ self.out2D, self.outpp2D, self.out1D, self.outinfo ])
        self.box = VBox([   self.header,
                            self.tabs
                        ])
        # self.box = VBox([self.title,
        #                 self.FC,
        #                 HBox([self.bdisp2D, self.bpp2D, self.bdisp1D])
        #                 ])
        if style:
            FI.injectcss()
        if show:
            display(self.box)

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
    def title(self):
        return str(self.filechooser.name)

    def load2D(self, e):
        "create 2D object and display"
        self.wait()
        with self.waitarea:
            print('Please wait while loading...')
#        self.outpp2D.clear_output(wait=True)
        fullpath = self.selected
        try:
            self.MR2D = MR_interact(fullpath, 
                report=False, show=False, Debug=self.debug)
        except: # (FileNotFoundError NoSuchNodeError):
            self.MR2D = None
            self.done()
            with self.waitarea:
                print('Error while loading',self.selected, 'file not found or wrong format')
                self.waitarea.clear_output(wait=True)
            return
        with self.out2D:
            clear_output(wait=True)
            self.MR2D.show()
#                display(self.MR2D.box)
#                display(self.MR2D.sbox)
        with self.out1D:
            clear_output(wait=True)
            self.lci = LC1D(self.MR2D, Debug=self.debug)
#            self.MR2D.I1D()
        # with self.outpp2D:
        #     display(self.MR2D.box)  # copie of the main pane
        #     display(self.MR2D.sbox)
        with self.outinfo:
            clear_output(wait=True)
            self.MR2D.report()
        self.tabs.selected_index = 1
        self.done()
        self.waitarea.clear_output()
