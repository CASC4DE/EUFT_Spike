# -*- coding: utf-8 -*-
"""
program to import sets of LC-MS spectra
processing is done on the fly
It creates and returns a HDF5 file containing the data-set
"""
import sys

from xml.etree import cElementTree as ET

from spike.File.Solarix import *
from spike.NPKData import TimeAxis
from spike.File import HDF5File as hf
from spike.util import progressbar as pg
from spike.util import widgets
from spike.NPKData import copyaxes

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
        elif si1>=1024:
            si1 = si1//2
        if si2>= 8*1024:
            si2 = si2//4
        elif si2>=1024:
            si2 = si2//2
        allsz.append((si1,si2))
    return allsz

def Import_and_Process_LC(folder, outfile = "LC-MS.msh5", compress=False, downsample=True):
    """
    Entry point to import sets of LC-MS spectra
    processing is done on the fly
    It creates and returns a HDF5 file containing the data-set
    
    compression is active if (compress=True).
    downsample is applied if (downsample=True).
    These two parameters are efficient but it takes time.
    """
    parfilename = locate_acquisition(folder)
    params = read_param(parfilename)
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
            spectre.zeroing(sigma*3).eroding()
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
                    spectre.zeroing(sigma*3).eroding()
                    maxvalues[idt+1] = max( maxvalues[idt+1], spectre.absmax )   # compute max (0 is full spectrum)
                    datai.buffer[ii1,:] = spectre.buffer[:]

            pbar.update(i1)
        # flush the remaining packet
        maxvalues[0] = max( maxvalues[0], abs(packet[:ipacket,:].max()) )
        data.buffer[i1-ipacket:i1,:] = packet[:ipacket,:]
    # store maxvalues in the file
    HF.store_internal_object(maxvalues, h5name='maxvalues')
    # then write projection as 'projectionF2'
    proj = FTICRData(dim = 1)
    proj.axis1 = data.axis2.copy()
    HF.create_from_template(proj, group='projectionF2')
    proj.buffer[:] =  projection.buffer[:]
    pbar.finish()
    HF.flush()
    return data

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
    parser.add_argument('importBrukfolder', help='input folder that contains the sample to process')
    parser.add_argument('outputfile', help='output file in msh5 format')
    parser.add_argument('-d', '--paramfile', help='optional parameter file in mscf format')
    parser.add_argument('--doc', action='store_true', help="print a description of the program")
    parser.add_argument('-c', '--compress', action='store_true', help="option to apply file compression, default is False")
    parser.add_argument('-ds', '--downsampling', action='store_true', help="option to apply downsampling to improve access speed, default is False")
    parser.add_argument('-e', '--erase', action='store_true', help="creates a new output file if it already exists, default is False")
    parser.add_argument('-n', '--dry',  action='store_true', help="list parameter and do not run the Import")

    args = parser.parse_args()

    if args.doc:
        print(__doc__)
        sys.exit(0)

    if args.paramfile is not None:
        print("should read", args.paramfile )
    else:
        infilename = args.importBrukfolder
        outputfile = args.outputfile
        compression = args.compress
        downSampling = args.downsampling
        erase = args.erase

    if args.dry:
        print(sys.argv[0],' dry run:')
        print('------------------------')
        for nm in ("infilename", "outputfile", "compression", "downSampling", "erase", "paramfile"):
            print(nm, getattr(args,nm))
        print('------------------------')
        sys.exit(0)
    if os.path.isfile(outputfile):
        if erase == False:
            sys.exit("File already exists, type a different output file name or erase the existing one")
        else:
            print("Output file will be rewritten")

    t0 = time.time()
    Set_Table_Param()
    d = Import_and_Process_LC(infilename, outfile=outputfile, compress=compression, downsample=downSampling)
    elaps = time.time()-t0
    print('Processing took %.2f minutes'%(elaps/60))

if __name__ == '__main__':
    sys.exit(main())
