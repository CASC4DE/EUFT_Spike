"""
various utilities for processing un interactive program
"""
""
import sys, os
import os.path as op
from pprint import pprint
from collections import namedtuple
from functools import partial
from pprint import pprint
from spike.NPKData import _NPKData as npkd

Apodisation = namedtuple('Apodisation', ['name', 'function'])


def loadjson(filename):
    """
    load a json file skipping   # comments and   // comments
    """
    import json
    c = []
    with open("config.json") as F:
        for l in F:
            l=l.strip()
            if not (l.startswith('#') or l.startswith('//')):
                c.append(l)
    return json.loads("".join(c))

####################
# ##   NMR  #########
# ###################

def _process_1d(audit,p_in_arg,f_in,f_out,inputfilename,outputfilename):
    """
    FT processing of a 1D FID
    
    based on pre_ft_1d() ft_1d() post_ft_1d()
    """
    p_in = build_dict(("pre_ft_1d","ft_1d","post_ft_1d"),p_in_arg)

    # Pre ft phase
    audittrail( audit, "phase", "FID preparation phase")
    pre_ft_1d( audit, inputfilename, "memory", p_in, f_in, f_out)
    
    # ft phase
    audittrail( audit, "phase", "Spectral analysis phase")
    ft_1d( audit, "memory", "memory", p_in, f_in, f_out)

    # Post ft phase
    audittrail( audit, "phase", "Post processing phase")
    post_ft_1d( audit, "memory", outputfilename, p_in, f_in, f_out)


def set_task(*arg , **kw):
    print('Task:', *arg, **kw)

    return (auditfilename)
def auditget(auditfilename="audit_trail.txt", append=True):
    "get acces to the auditfile (open the file) and returns file descriptor"
    if (auditfilename=="mute"):
        auditfile = sys.stdout
    elif os.path.exists(auditfilename) and append:
        auditfile = open(auditfilename,"a")
    else:
        auditfile = open(auditfilename,"w")
    return auditfile
def auditrelease(auditfile):
    "closes the audit file"
    if auditfile != sys.stdout:
        auditfile.close()
def auditclose(auditfilename="audit_trail.txt"):
    "sign the audit file"
    import hashlib
    if auditfilename != "mute":
        text = open(auditfilename,'rb').read()
        with open(auditfilename,'a') as F:
            F.write("\n        SHA256: ")
            F.write(hashlib.sha256(text).hexdigest())
            F.write('\n\n')
def auditinitial( auditfilename="audit_trail.txt",title="NPK Processing",append=True):
    """ initialize the audit trail file
    
    auditfilename is the name of the audit file
    if the file does not exist it is created and initialized,
    if append ==1 and if the file exists, content will be added to it, this is the default behaviour
    """
    import spike.version
    import time
    def pr(*arg):
       print(*arg, file=auditfile) 
    auditfile = auditget(auditfilename=auditfilename, append=append)
    pr("___________________________________")
    pr("#",title)
    pr("- date: **%s**"%time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime()))
    pr("\n## Processing conditions")
    pr("- working directory: **%s**"%os.path.abspath(os.curdir))
    pr("- SPIKE kernel version: **%s** rev **%s** dated %s"%(spike.version.version, spike.version.revision,  spike.version.rev_date))
    pr(" ")
    return auditfile

def audittrail(audit, mode, *arg):
    """ management of the audit trail.
    
    first argument determines action : open close phase text
    arguments depends on the action
    
    eg:
    audit = auditinitial(filename, "title in audit file")
        opens the audit trail - use the argument as title
    audittrail(audit, close)
        closes the audit trail
    audittrail(audit, phase, "title of phase")
        start a new phase, creates a new heading in the audit trail
    audittrail(audit, text, "text to write in audit trail", (parameter_name, parameter_value,) ...)
        writes in the audit trail

    if text is available on several arguments, several lines are displayed,
    in this case, the first arguments is the text/title, and the following arguments are
    by pair, with parameter_name  parameter_value 
    """
    def pr(*argpr):
       print(*argpr, file=audit)
    if mode == "close":
        if audit != sys.stdout:
            audit.close()
    elif mode == "phase":
        pr('\n## %s phase'%(arg[0]))
    elif mode == "text":
        argl = list(arg)
        pr('\n### %s '%(argl.pop(0),))
        while argl:
            k = argl.pop(0)
            try:
                v = "%s"%(argl.pop(0),)
            except:
                v = "*missing value*"
            pr('- %s: %s'%(k,v))

##################### PROCESSiNG ###################
NMR_Apod = {}
NMR_Apod['None'] =        Apodisation('no apodisation', partial(npkd.apod_em, lb=0.0))
NMR_Apod['standard1H'] =  Apodisation('standard 1H  em 0.3Hz', partial(npkd.apod_em, lb=0.3))
NMR_Apod['standard13C'] = Apodisation('standard 13C em 3Hz', partial(npkd.apod_em, lb=3.0))

# static definition of default processing parameters
procparam_NMR = {}
procparam_NMR['center_fid'] = True
procparam_NMR['apodisations'] = NMR_Apod
procparam_NMR['apod_todo'] = 'standard1H'

def process_nmr1d(data, parameters):
    #pre_ft_1d
    audit = auditinitial(title="NMR processing",append=False)
    if False:
        audittrail( audit, "phase",audit, "FID noise evaluation")
        last = 0.2 # p_in["fid_noise_zone"]        # usually 0.2 which means last 20 % of data set
        a,b = (1-last)*data.cpxsize1, data.cpxsize1
        shift = data.mean(zone=(a,b))
        noise = data.std(zone=(a,b))
        audittrail( audit, "text", "stat analysis of FID",
            "offset",shift,
            "noise", noise)

    if False: # (key_is_true(p_in,"dc_offset")):
        audittrail( audit, "phase","DC-offset correction")
        data -= shift
        audittrail( audit, "text", "vertical shift of FID","offset", -shift)

    if True: #( key_is_true(p_in,"apodize") and (p_in["apodisation"] != "none")):
        audittrail( audit, "phase","Apodisation")
        lb = 0.3
        # apodise(p_in.raw("apodisation"))
        data.apod_em(0.3)
        audittrail( audit, "text", "FID apodisation before FT",
                   "function", lb)

    audittrail( audit, "phase","fourier-transform")
    data.zf(4)
    data.ft_sim()
    data.bk_corr()
    audittrail( audit, "phase", "Post processing phase")
    data.apmin()  # chaining  apodisation - zerofill - FT - Bruker correction - autophase
    data.set_unit('ppm')  # chain  set to ppm unit - and display
    print("final data-set",data)
    return data

#########################################################################
# ###### MS
# ########################################################################
MS_Apod = {}
MS_Apod['None'] = Apodisation('no apodisation',  partial(npkd.apod_em, lb=0.0))
MS_Apod['hamming'] = Apodisation('Hamming', partial(npkd.hamming))
MS_Apod['hanning'] = Apodisation('Hanning', partial(npkd.hanning))
MS_Apod['kaiser3.5'] = Apodisation('kaiser, beta=3.5', partial(npkd.kaiser, beta=3.5))
MS_Apod['kaiser5'] = Apodisation('kaiser, beta=5', partial(npkd.kaiser, beta=5.0))
MS_Apod['kaiser6'] = Apodisation('kaiser, beta=6', partial(npkd.kaiser, beta=6.0))
MS_Apod['kaiser8'] = Apodisation('kaiser, beta=8', partial(npkd.kaiser, beta=8.0))

# static definition of default processing parameters
procparam_MS = {
    'center_fid': "Yes",
    'apodisations': MS_Apod,         # list of defined apodisation
    'apod_todo': 'hamming',          # default one
    'zf_level': 2, # 4 !
    'baseline_correction': {
        'None': 'No baseline correction',
        'offset': 'Offset correction'
        },
    'baseline_todo': 'offset',
    'grass_noise': {
        'None': 'Never apply post-FT cleaning',
        'storage': 'Only when storing output file (smaller files)',
        'auto': 'Automatically after Fourier-transform'
        },
    'grass_noise_todo': 'storage',
    'grass_noise_level': 3,
    'peakpicking': {
        'manual': 'Manually on-demand',
        'auto':   'Automatically after Fourier-transform'
        },
    'peakpicking_todo': 'auto',
    'peakpicking_noise_level': 3,
    'centroid': "Yes",
}

def process_ms1d(data, parameters, verbose=False):
    #pre_ft_1d
    if verbose: pprint(parameters)
    audit = auditinitial(title="MS processing", append=False)
    audittrail( audit, "text", str(data))

    if True:
        audittrail( audit, "phase", "Pre processing")
        last = 0.2 # p_in["fid_noise_zone"]        # usually 0.2 which means last 20 % of data set
        a,b = (1-last)*data.cpxsize1, data.cpxsize1
        shift = data.mean(zone=(a,b))
        noise = data.std(zone=(a,b))
        audittrail( audit, "text", "stat analysis of FID",
            "offset",shift,
            "noise", noise)
    # dc-offset
    if parameters['center_fid'] == 'Yes':
        data.buffer -= shift
        audittrail( audit, "text", "vertical shift of FID",
            'center_fid', parameters['center_fid'],
            "offset", -shift)

    audittrail( audit, "phase","Spectral Analysis")
    # Apod
    if True: #( key_is_true(p_in,"apodize") and (p_in["apodisation"] != "none")):
        todo = parameters['apod_todo']
        f = parameters['apodisations'][todo].function
        f(data)
        audittrail( audit, "text", "FID apodisation before FT",
                   "apod_todo", parameters['apodisations'][todo].name)
    # FT
    initial = data.size1
    data.zf(int(parameters['zf_level']))
    data.rfft()
    audittrail( audit, "text", "Fourier Transform",
                "initial size", initial,
                "zf_level", parameters['zf_level'],
                "Fourier_algo", 'rfft',

                "final size", data.size1)
    audittrail( audit, "phase", "Post processing")
    data.modulus()
    mu, sigma = data.robust_stats( iterations=10 )
    data.noise = sigma
    # Baseline
    if parameters['baseline_todo'] == 'None':
            print ('No baseline correction')
    elif parameters['baseline_todo'] == 'offset':
            data.buffer -= mu
            audittrail( audit, "text", "Baseline correction",
                "mean offset", mu)
    # grass noise
    if parameters['grass_noise_todo'] == 'auto':
        data.zeroing(parameters['grass_noise_level']*data.noise)
        data.eroding()
        audittrail( audit, "text", "grass noise removal",
            "noise threshold", parameters['grass_noise_level'])

    data.set_unit('m/z')
    audittrail( audit, "text", "final",
                "modulus", "applied",
                "unit", 'm/z',
                "calibration - A", data.axis1.calibA,
                "calibration - B", data.axis1.calibB,
                "calibration - C", data.axis1.calibC,
                "spectrum final size", data.size1)
    auditrelease(audit)
    auditclose()
    if parameters['peakpicking_todo'] == 'auto':
        parameters['zoom'] = None
        peakpick_ms1d(data, parameters)
    if verbose: print("final data-set",data)
    return data

def peakpick_ms1d(data, parameters):
    "do the peak-picking calling pp().centroid()"
    #self.spec.clear_output(wait=True)
    audit = auditinitial(title="MS post-processing", append=True)
    audittrail( audit, "text", str(data))
    audittrail( audit, "phase","Peak-Picking")
    # check is dataset was compressed
    b = data.get_buffer().real
    test = b[b != 0.0 ]
    if (len(b)-len(test))/len(b) >0.1 : # more than 10% zeroed !
        audittrail( audit, "text","dataset is compressed - noise estimate is approximate")
        test = test[ (test-test.mean()) < 5*test.std() ]
        threshold = test.std()*float(parameters['peakpicking_noise_level'])/3
        data.set_unit('m/z').peakpick(threshold=threshold, verbose=False, zoom=parameters['zoom'])
    else:
        data.set_unit('m/z').peakpick(autothresh=float(parameters['peakpicking_noise_level']), verbose=False, zoom=parameters['zoom'])
    if parameters['centroid'] == 'Yes':
        data.centroid()
    # compute unique file name 
    if op.isdir(data.fullpath):     # typically *.d
        fnamehi = op.join( data.fullpath,'peaklist_%d.html')
        fnameci = op.join( data.fullpath,'peaklist_%d.csv')
    else:                           # typically *.msh5
        fnamehi = op.splitext(data.fullpath)[0] + '_peaklist_%d.html'
        fnameci = op.splitext(data.fullpath)[0] + '_peaklist_%d.csv'
    # find a slot
    i = 1
    while op.exists(fnamehi%i) or op.exists(fnameci%i):
        i += 1
    fnameh = fnamehi%i
    fnamec = fnameci%i
    print(fnameh)
    # create files
    with open(fnameh,'w') as F:
        F.write( data.pk2pandas(full=False).to_html() )
    with open( fnamec,'w') as F:
        F.write( data.pk2pandas(full=False).to_csv() )
    path_list = fnamec.split(os.sep)
    audittrail( audit, "text", "Peak-Picking",
                   "threshold above noise level", parameters['peakpicking_noise_level'],
                   "zoom", parameters['zoom'],
                   "number of detected peaks", len(data.peaks),
                   "output file:", op.join(path_list[-2], path_list[-1]))
    auditrelease(audit)
    auditclose()
    print(len(data.peaks), 'Peaks detected')
    return data
