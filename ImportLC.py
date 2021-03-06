# -*- coding: utf-8 -*-
"""
program to import sets of LC-MS spectra
processing is done on the fly
It creates and returns a HDF5 file containing the data-set
"""
import sys
import os
import math
import array
import numpy as np
from xml.etree import cElementTree as ET


def Set_Table_Param():
#    if debug>0: return
    import tables
    tables.parameters.CHUNK_CACHE_PREEMPT = 1
    tables.parameters.CHUNK_CACHE_SIZE = 100*1024*1024
    tables.parameters.METADATA_CACHE_SIZE  = 100*1024*1024
    tables.parameters.NODE_CACHE_SLOTS = 100*1024*1024
    #tables.parameters.EXPECTED_ROWS_EARRAY = 100
    #tables.parameters.EXPECTED_ROWS_TABLE =100
    #tables.parameters.MAX_THREADS = 8
    #tables.parameters.PYTABLES_SYS_ATTRS = False


def import_scan(filename):
    """
    Read scan.xml file and return the minutes, tic and max peak lists. Exit with error if scan.xml file doesn't exists.
    """
    if os.path.isfile(filename):
        f = open(filename, "r")
    else:
        sys.exit("Cannot find scan.xml file in input folder")
    data =f.read()
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
    f.close()
    return (minutes_list, tic_list, maxpeak_list)

def comp_sizes(si1, si2):
    """
    computes sizes of smaller version of dataset
    """
    allsz = []
    while si1>1024 or si2>1024:
        if si1>=2048:
            si1 = si1//4
        elif si1>1024:
            si1 = si1//2
        if si2>= 4*1024:
            si2 = si2//4
        elif si2>1024:
            si2 = si2//2
        allsz.append((si1,si2))
    return allsz

def Import_and_Process_LC(folder, outfile = "LC-MS.msh5", compress=False, comp_level=3.0, downsample=True, dparameters=None):
    """
    Entry point to import sets of LC-MS spectra
    processing is done on the fly
    It creates and returns a HDF5 file containing the data-set
    
    compression is active if (compress=True).
    comp_level is the ratio (in x sigma) under which values are set to 0.0
    downsample is applied if (downsample=True).
    These two parameters are efficient but it takes time.

    dparameters if present, is a dictionnary copied into the final file as json 
    """
    from spike.File import Solarix, Apex 
#    from spike.File.Solarix import locate_acquisition, read_param
    from spike.NPKData import TimeAxis, copyaxes
    from spike.File import HDF5File as hf
    from spike.util import progressbar as pg
    from spike.util import widgets
    from spike.FTICR import FTICRData
    for _importer in (Solarix, Apex):
        try:
            parfilename = _importer.locate_acquisition(folder)
            params = _importer.read_param(parfilename)
            sizeF2 = int(params["TD"])
            importer = _importer
            break
        except:
            print("***************************************")
            print(params)
        else:
            raise Exception("could  not import data-set - unrecognized format")
    # get chromatogram
    minu, tic, maxpk = import_scan( os.path.join(folder,"scan.xml") )   
    # Import parameters : size in F1 and F2    
    sizeF1 = len(minu)
    sizeF2 = int(params["TD"])
    if os.path.isfile(os.path.join(folder,"ser")):
        fname = os.path.join(folder, "ser")
    else:
        raise Exception("You are dealing with 1D data, you should use Import_1D")
    #size, specwidth,  offset, left_point, highmass, calibA, calibB, calibC, lowfreq, highfreq
    data = FTICRData( dim=2 )   # create dummy LCMS
    data.axis1 = TimeAxis(size=sizeF1, tabval=np.array(minu), importunit="min", currentunit='min' )    
    data.axis2.size = 1*sizeF2    # The processing below might change the size, so we anticipate here !    
    data.axis2.specwidth = float(params["SW_h"])   
    found = False    # search for excitation bandwidth
    try:
        data.axis2.lowfreq, data.axis2.highfreq = read_ExciteSweep(locate_ExciteSweep(folder))
        found = True
    except:
        pass
    if not found:
        try:
            data.axis2.highfreq = float(params["EXC_Freq_High"])
        except:
            data.axis2.highfreq = data.axis2.calibA/float(params["EXC_low"])  # on Apex version
        try:
            data.axis2.lowfreq = float(params["EXC_Freq_Low"])
        except:
            data.axis2.lowfreq = data.axis2.calibA/float(params["EXC_hi"])  # on Apex version

    data.axis2.highmass = float(params["MW_high"])
    data.axis2.left_point = 0
    data.axis2.offset = 0.0
    data.axis2.calibA = float(params["ML1"])
    data.axis2.calibB = float(params["ML2"])
    data.axis2.calibC = float(params["ML3"])
    if not math.isclose(data.axis2.calibC,0.0):
        print('Using 3 parameters calibration,  Warning calibB is -ML2')
        data.axis2.calibB *= -1

    data.params = params   # add the parameters to the data-set
    HF = hf.HDF5File(outfile,"w")
    if compress:
        HF.set_compression(True)
    HF.create_from_template(data, group='resol1')
    HF.store_internal_object(params, h5name='params')    # store params in the file
    # then store files xx.methods and scan.xml
    HF.store_internal_file(parfilename)
    HF.store_internal_file( os.path.join(folder,"scan.xml") )
    try:
        HF.store_internal_file( locate_ExciteSweep(folder) )
    except:
        print('ExciteSweep file not stored')
    data.hdf5file = HF    # I need a link back to the file in order to close it 

    # Start processing - first computes sizes and sub-datasets
    print(data)
    datalist = []   # remembers all downsampled dataset
    maxvalues = [0.0]  # remembers max values in all datasets - main and downsampled
    if downsample:
        allsizes = comp_sizes(data.size1, data.size2)
        for i, (si1,si2) in enumerate(allsizes):
            datai = FTICRData(dim = 2)
            copyaxes(data,datai)
            datai.axis1.size = si1
            datai.axis2.size = si2
            HF.create_from_template(datai, group='resol%d'%(i+2))
            datalist.append(datai)
            maxvalues.append(0.0)

    # Then go through input file
    if sys.maxsize  == 2**31-1:   # the flag used by array depends on architecture - here on 32bit
        flag = 'l'              # Apex files are in int32
    else:                       # here in 64bit
        flag = 'i'              # strange, but works here.
    spectre = FTICRData(shape=(sizeF2,))               # to handle FT
    projection = FTICRData(buffer=np.zeros(sizeF2))    # to accumulate projection
    projection.axis1 = data.axis2.copy()
    Impwidgets = ['Importing: ', widgets.Percentage(), ' ', widgets.Bar(marker='-',left='[',right=']'), widgets.ETA()]
    pbar = pg.ProgressBar(widgets=Impwidgets, maxval=sizeF1, fd=sys.stdout).start()
    
    with open(fname,"rb") as f:
        ipacket = 0
        szpacket = 10
        packet = np.zeros((szpacket,sizeF2))   # store by packet to increase compression speed
        for i1 in range(sizeF1):
            absmax = 0.0
            #print(i1, ipacket, end='  ')
            tbuf = f.read(4*sizeF2)
            if len(tbuf) != 4*sizeF2:
                break
            abuf = np.array(array.array(flag,tbuf),dtype=float)
            # processing
            spectre.set_buffer(abuf)
            spectre.adapt_size()
            spectre.hamming().zf(2).rfft().modulus()  # double the size
            mu, sigma = spectre.robust_stats(iterations=5)
            spectre.buffer -= mu
            if compress:
                spectre.zeroing(sigma*comp_level).eroding()
            packet[ipacket,:] = spectre.buffer[:]  # store into packet
            np.maximum(projection.buffer, spectre.buffer, out=projection.buffer)  # projection
            if (ipacket+1)%szpacket == 0:          # and dump every szpacket
                maxvalues[0] = max( maxvalues[0], abs(packet.max()) )   # compute max
                data.buffer[i1-(szpacket-1):i1+1,:] = packet[:,:]  # and copy
                packet[:,:] = 0.0
                ipacket = 0
            else:
                ipacket += 1
            # now downsample
            for idt, datai in enumerate(datalist):
                if i1%(sizeF1//datai.size1) == 0:   # modulo the size ratio
                    ii1 = (i1*datai.size1) // sizeF1
                    spectre.set_buffer(abuf)
                    spectre.adapt_size()
                    spectre.chsize(datai.size2).hamming().zf(2).rfft().modulus()
                    mu, sigma = spectre.robust_stats(iterations=5)
                    spectre.buffer -= mu
                    if compress:
                        spectre.zeroing(sigma*comp_level).eroding()
                    maxvalues[idt+1] = max( maxvalues[idt+1], spectre.absmax )   # compute max (0 is full spectrum)
                    datai.buffer[ii1,:] = spectre.buffer[:]

            pbar.update(i1)
        # flush the remaining packet
        maxvalues[0] = max( maxvalues[0], abs(packet[:ipacket,:].max()) )
        data.buffer[i1-ipacket:i1,:] = packet[:ipacket,:]
    # store maxvalues in the file
    HF.store_internal_object(maxvalues, h5name='maxvalues')
    if dparameters is not None:
        HF.store_internal_object(dparameters, h5name='import_parameters')

    # then write projection as 'projectionF2'
    proj = FTICRData(dim = 1)
    proj.axis1 = data.axis2.copy()
    HF.create_from_template(proj, group='projectionF2')
    proj.buffer[:] =  projection.buffer[:]
    pbar.finish()
    HF.flush()
    return data

class Proc_Parameters(object):
    """this class is a container for processing parameters"""
    def __init__(self, configfile = None):
        "initialisation, see import.mscf for comments on parameters"
        #from spike.NPKConfigParser import NPKConfigParser
        from configparser import ConfigParser as NPKConfigParser
        # processing
        self.outfile = None
        self.infilename = None
        self.compression = True
        self.compress_level = 3.0
        self.downSampling = True
        self.erase = True
        self.paramfile = None
        if configfile is not None:
            self.paramfile = configfile
            cp = NPKConfigParser()
            print('parameter file is ', configfile)
            cp.read_file(open(configfile,'r'))
            self.outfile = cp['processing'].get("outfile", None)
            self.infilename = cp['processing'].get("importBrukfolder", None)
            self.compression = cp['processing'].getboolean("compress_outfile", "True")
            self.compress_level = cp['processing'].getfloat("compress_level", 3.0)
            self.downSampling = cp['processing'].getboolean("downsampling", "True")
            self.erase = cp['processing'].getboolean("erase", "True")
    def todic(self):
        "export to dictionary"
        dd = {}
        for nm in dir(self):
        #("paramfile", "infilename", "outfile", "compression", "compress_level", "downSampling", "erase"):
            if not nm.startswith('_'):
                val = getattr(self,nm)
                if not callable(val):
                    dd[nm] = val
        return dd
    def report(self):
        "print a report"
        print('------------------------')
        for (nm,val) in self.todic().items():
            print(nm, ':', val)
        print('------------------------')
    @property
    def fulloutname(self):
        if self.infilename is None or self.outfile is None:
            return None
        else:
            return os.path.join(self.infilename, self.outfile)
    
def main():
    """
    python ImportLC.py [options] importBrukfolder.d outputfile.msh5
    options:
    -c : do compression (True or False, default False)
    -ds : perform downsampling (True or False, default False)
    -e : erase previous output file if it already exists (True or False, default False: if file exists returns error)
    """
    import argparse
    import time
    import os.path

    # Parse and interpret options.
    parser = argparse.ArgumentParser()
    parser.add_argument('importBrukfolder', nargs='?', default=None,
        help='input folder that contains the experiment to process - optional if parameter file is provided')
    parser.add_argument('outfile', nargs='?', default=None, 
        help='output file in msh5 format, relative to importBrukfolder - optional')
    parser.add_argument('-d', '--paramfile', help='optional parameter file in mscf format')
    parser.add_argument('--doc', action='store_true', help="print a description of the program - required if importBrukfolder is missing")
    parser.add_argument('-c', '--compress', action='store_true', help="option to apply file compression, default is False")
    parser.add_argument('-cl', '--compress_level', type=float, help="compression level - default is 3.0")
    parser.add_argument('-ds', '--downsampling', action='store_true', help="option to apply downsampling to improve access speed, default is False")
    parser.add_argument('-e', '--erase', action='store_true', help="creates a new output file if it already exists, default is False")
    parser.add_argument('-n', '--dry',  action='store_true', help="list parameter and do not run the Import")


    args = parser.parse_args()

    if args.doc:
        print(__doc__)
        sys.exit(0)


    # If from parameter file
    if args.paramfile is not None:
        param = Proc_Parameters(args.paramfile)
        if param.infilename is None:
            param.infilename = os.path.dirname(args.paramfile)
        if param.outfile is None:
            param.outfile = os.path.splitext( os.path.basename(args.paramfile))[0] + '.msh5'
    # if from line arguments
    else:
        param = Proc_Parameters()
        param.compression = args.compress
        param.compress_level = args.compress_level
        param.downSampling = args.downsampling
        param.erase = args.erase
        param.infilename = args.importBrukfolder
        param.outfile = args.outfile
        if param.outfile is None:
            param.outfile = 'dataset.msh5'


    try:
        if os.path.isfile(param.fulloutname):
            if param.erase == False:
                sys.exit("File already exists, type a different output file name or erase the existing one")
            else:
                print("Output file will be rewritten")
    except:
        print("****** Error in command line\n", file=sys.stderr)  # happens if no arg at all
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.dry:
        print(sys.argv[0],'dry run:')
        param.report()
        sys.exit(0)

    t0 = time.time()
    Set_Table_Param()
    d = Import_and_Process_LC(param.infilename, outfile=param.fulloutname,
        compress=param.compression, comp_level=param.compress_level, downsample=param.downSampling)
    elaps = time.time()-t0
    print('Processing took %.2f minutes'%(elaps/60))

if __name__ == '__main__':
    sys.exit(main())
