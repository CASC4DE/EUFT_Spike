#!/usr/bin/env python 
# encoding: utf-8

"""
A tool to display FT-ICR data-sets

to be embedded in jupyter notebook

MAD march 2020

This version requires ipympl (see: https://github.com/matplotlib/jupyter-matplotlib )
and the notebook to be opened with %matplotlib widget
"""
import os.path as op
from pathlib import Path
import tables
import matplotlib.pyplot as plt
from ipywidgets import interact, fixed, HBox, VBox, GridBox, Label, Layout, Output, Button
import ipywidgets as widgets
from IPython.display import display, Markdown, HTML, Image
import numpy as np

from spike import FTICR
from spike.NPKData import flatten, parsezoom
from spike.FTMS import FTMSData
from spike.FTICR import FTICRData
from spike.File import BrukerMS
import utilities as U

# REACTIVE modify callback behaviour
# True is good for inline mode / False is better for notebook mode
REACTIVE = True
HEAVY = False
DEBUG = False

SIZEMAX = 8*1024*1024       # largest zone to display
NbMaxDisplayPeaks = 200      # maximum number of peaks to display at once

# TOOLS FOR 1D FTICR
class FileChooser(VBox):
    """a simple chooser for Jupyter for selecting *.d directories"""
    def __init__(self, base='FT-ICR'):
        super().__init__()
        filelistraw = [str(i.relative_to(base)) for i in Path(base).glob('**/*.d')]
        filelistproc = [str(i.relative_to(base)) for i in Path(base).glob('**/*.msh5')]
        flist = ['   --- raw ---']
        flist += filelistraw
        flist.append('   --- processed ---')
        flist += filelistproc
        self.selec = widgets.Select(options=flist,layout={'width': 'max-content'})
        self.children  = [widgets.HTML('<b>Choose one experiment</b>'), self.selec ]

class Dataproc:
    "a class to hold a data set and to process it"
    def __init__(self, data):
        self.data = data    # the fid
        self.DATA = None    # the spectrum
        self.procparam = U.procparam_MS
        self.procparam["peakpicking_todo"] = "manual"
        self.procparam['zoom'] = None
        self.procparam['peakpicking_noise_level'] = 10
        self.procparam['centroid'] = "No"

    def process(self):
        if self.data.dim == 1:
            self.DATA = U.process_ms1d(self.data.copy(), self.procparam)
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
    def __init__(self, show=True, base='FT-ICR'):
        # header
        #   filechooser
        self.base = 'FT-ICR'
        self.filechooser = FileChooser(self.base)
        self.datap = None
        self.MAX_DISP_PEAKS = NbMaxDisplayPeaks

        #   buttons
        #       load
        self.bload = Button(description='Load',layout=Layout(width='15%'),
                button_style='success', tooltip='load and display experiment')
        self.bload.on_click(self.load)
        #       FT
        self.bproc = Button(description='Process',layout=Layout(width='15%'),
                button_style='success', tooltip='Fourier transform of the fid')
        self.bproc.on_click(self.process)
        #       pp
        self.bpeak = Button(description='Peak Pick',layout=Layout(width='15%'),
                button_style='success', tooltip='load and display experiment')
        self.bpeak.on_click(self.peakpick)

        # GUI set-up and scene
        # tools 
        self.header = Output()
        with self.header:
            self.waitarea = Output()
            self.buttonbar = HBox([self.bload, self.bproc, self.bpeak, self.waitarea])
            display(Markdown('---\n# Select an experiment, and process'))
            display(self.filechooser)
            display(self.buttonbar)

        NODATA = HTML("<br><br><h3><i><center>No Data</center></i></h3>")
        # fid
        self.fid = Output()  # the area where 1D is shown
        with self.fid:
            display(NODATA)

        # spectrum
        self.out1D = Output()  # the area where 1D is shown
        with self.out1D:
            display(NODATA)

        # peaklist
        self.peaklist = Output()  # the area where peak list is shown
        with self.peaklist:
            display(NODATA)

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
        self.tabs.set_title(1, 'spectrum')
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
        if show:
            display(self.box)

    def showinfo(self):
        self.outinfo.clear_output()
        with self.outinfo:
            if self.datap == None:
                display(HTML("<br><br><h3><i><center>No Data</center></i></h3>"))
            else:
                display( Markdown("# Raw Dataset\n%s\n"%(self.selected,)) )
                print(self.datap.data)
                if self.datap.DATA != None:
                    with open('audit_trail.txt','r') as F:
                        display(Markdown(F.read()))
    def wait(self):
        "show a little waiting wheel"
        with open("icon-loader.gif", "rb") as F:
            with self.waitarea:
                self.wwait = widgets.Image(value=F.read(),format='gif',width=40)
                display(self.wwait)
    def done(self):
        "remove the waiting wheel"
        self.wwait.close()
    @property
    def selected(self):
        return self.filechooser.selec.value

    def load(self, e):
        "load 1D fid and display"
        self.fid.clear_output(wait=True)
        fullpath = op.join(self.base,self.selected)
        try:
            data = BrukerMS.Import_1D(fullpath)
        except:
            with self.waitarea:
                print('Error while loading',self.selected)
                self.waitarea.clear_output(wait=True)
            return
        data.filename = self.selected
        data.fullpath = fullpath
        data.set_unit('sec')
        with self.fid:
            data.display(title=self.selected)
        self.datap = Dataproc(data)
        self.showinfo()
        self.param2form(self.datap.procparam)
        self.outform.clear_output()
        with self.outform:            # refresh param form
            display(self.form)
        self.tabs.selected_index = 0

    def process(self,e):
        "do the FT"
        if self.datap == None:
            with self.waitarea:
                print('Please load a dataset first')
                self.waitarea.clear_output(wait=True)
            return
        self.wait()
        self.out1D.clear_output(wait=True)
        self.form2param()
        self.datap.process()
        with self.out1D:
            self.datap.DATA.display(title=self.selected)
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
        self.datap.peakpick()
        with self.out1D:
            self.datap.DATA.display_peaks(peak_label=True ,NbMaxPeaks=self.MAX_DISP_PEAKS)
        with self.peaklist:
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
        
        chld.append( widgets.FloatLogSlider(value=3,min=0,max=3,description='peakpicking noise level', layout=ly, style=style) )

        chld.append( widgets.RadioButtons(options=['Yes','No'],value='Yes',description='centroid',layout=ly, style=style))

        chld.append( widgets.IntSlider(value=self.MAX_DISP_PEAKS,min=10,max=10000,description='max peak displayed', layout=ly, style=style) )


        self.form = widgets.VBox(chld)
    def _paramform(self):
        "draw the processing parameter form - Obsolete"
        codes = {
            'apod_todo' : 'apodisations',
            'baseline_todo': 'baseline_correction',
            'peakpicking_todo': 'peakpicking',
            'grass_noise_todo': 'grass_noise'
        }
        codelist = tuple(codes.keys())
        codelist
        chld = []
        ly = Layout(width='50%')
        style = {'description_width': '30%'}
        for k,v in U.procparam_MS.items():
            if k in codelist:
                if isinstance(U.procparam_MS[codes[k]][v], U.Apodisation):
                    opt = U.procparam_MS[codes[k]].keys()
                else:
                    opt = [(v,k) for k,v in U.procparam_MS[codes[k]].items()]
                chld.append( widgets.Dropdown(options=opt,value=v,description=k, layout=ly, style=style) )
            else:
                if isinstance(v, str):
                    if v in ('Yes','No'):
                        chld.append( widgets.RadioButtons(options=['Yes','No'],value=v,description=k,layout=ly, style=style) )
                    else:
                        chld.append( widgets.Text(value=v, description=k, layout=ly, style=style ) )
                elif isinstance(v, int):
                    chld.append( widgets.FloatText(value=v, description=k,layout=ly, style=style ) )
        self.form = VBox(chld)

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


# ##################### 1D ##################
    def I1D(self):
        "show the 1D selector"
        self.r1D = None
        self.t1D = ''
        self.i1D = None
        self.check_fig1D()
        display(self.ext_box())

    def check_fig1D(self):
        if self.pltaxe1D is None:
            fg,ax = plt.subplots(figsize=(1.5*self.figsize[0], 0.75*self.figsize[0]))
            ax.text(0.1, 0.8, 'Empty - use "horiz" and "vert" buttons above')
            self.pltaxe1D = ax
            self.fig1D = fg

    def ext_box(self):
        "defines the interactive tools for 1D"
        wf = widgets.BoundedFloatText
        wi = widgets.BoundedIntText
        ref = self.data[0]
        style = {'description_width': 'initial'}
        lay = Layout(width='120px', height='30px')
        lay2 = Layout(width='50px', height='30px')
        self.z1 = wf( value=300.0, min=ref.axis1.lowmass, max=ref.highmass[0], description='F1', style=style, layout=lay)
        self.z2 = wf( value=300.0,  min=ref.axis2.lowmass, max=ref.highmass[1], description='F2', style=style, layout=lay)
        self.horiz = wi( value=1, min=1, max=20, style=style, layout=lay2)
        self.vert = wi( value=1, min=1, max=20, style=style, description="/", layout=lay2)
        def lrow(b, inc=0):
            rint = int(round(ref.axis1.mztoi(self.z1.value)))
            if inc !=0:
                rint += inc
            self.z1.value = ref.axis1.itomz(rint)
            if self.t1D == 'col':
                self.pltaxe1D.clear()
                self.r1D = None
            if self.b_accu.value == 'sum' and self.r1D is not None:
                self.r1D += ref.row(rint)
            else:
                self.r1D = ref.row(rint)
            self.t1D = 'row'
            self.i1D = rint
            self.display1D()
        def lrowp1(b):
            lrow(b,-1)
        def lrowm1(b):
            lrow(b,1)
        def lcol(b, inc=0):
            rint = int(round(ref.axis2.mztoi(self.z2.value)))
            if inc !=0:
                rint += inc
            self.z2.value = ref.axis2.itomz(rint)
            if self.t1D == 'row':
                self.pltaxe1D.clear()
                self.r1D = None
            if self.b_accu.value == 'sum' and self.r1D is not None:
                self.r1D += ref.col(rint)
            else:
                self.r1D = ref.col(rint)
            self.t1D = 'col'
            self.i1D = rint
            self.display1D()
        def lcolp1(b):
            lcol(b,-1)
        def lcolm1(b):
            lcol(b,1)
        def on_press(event):
            v = self.r1D.axis1.mztoi(event.xdata)
            if self.t1D == 'col':
                self.z1.value = v
            elif self.t1D == 'row':
                self.z2.value = v
        cids = self.fig1D.canvas.mpl_connect('button_press_event', on_press)

        self.bb('b_row', 'horiz', lrow, layout=Layout(width='60px'), tooltip='extract an horizontal row')
        self.bb('b_rowp1', '+1', lrowp1, layout=Layout(width='30px'), tooltip='next row up')
        self.bb('b_rowm1', '-1', lrowm1, layout=Layout(width='30px'), tooltip='next row down')
        self.bb('b_col', 'vert', lcol, layout=Layout(width='60px'), tooltip='extract a vertical col')
        self.bb('b_colp1', '+1', lcolp1, layout=Layout(width='30px'), tooltip='next col right')
        self.bb('b_colm1', '-1', lcolm1, layout=Layout(width='30px'), tooltip='next col left')
        self.b_accu = widgets.Dropdown(options=['off', 'graphic', 'sum'],
                value='off', description='Accumulate plots while scanning:', style=style)
        return VBox([ widgets.HTML('<h3>Extract 1D MS Spectrum going through given F1-F2 coordinates</h3>'),
                    HBox([widgets.HTML("<B>coord:</B>"),self.z1,
                          self.b_row, self.b_rowp1, self.b_rowm1, self.b_accu]),
                    HBox([widgets.HTML("<B>coord:</B>"),self.z2,
                          self.b_col, self.b_colp1, self.b_colm1])])
    def display1D(self):
        "display the selected 1D"
        if self.t1D == 'row':
            title = 'horizontal extract at F1=%f m/z (index %d)'%(self.z1.value, self.i1D)
            label = str(self.z1.value)
        elif self.t1D == 'col':
            title = 'vertical extract at F2=%f m/z (index %d)'%(self.z2.value, self.i1D)
            label = str(self.z2.value)
        if self.b_accu.value != 'graphic':
            self.pltaxe1D.clear()
            label = None
        self.r1D.display(xlabel='m/z', show=False, figure=self.pltaxe1D, new_fig=False, label=label, title=title)


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

