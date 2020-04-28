#!/usr/bin/env python
# coding: utf-8
"""
This programs goes throught a directory tree and adds a _vo metafile to the data-set lacking one
"""

import os, sys
import json
import numpy as np
from scipy.constants import N_A as Avogadro
from scipy.constants import e as electron
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime
from pathlib import Path


DEBUG = False
NO_ACTION = False

def metaname(foldname):
    "generate metafile filename from .d filename"
    base = os.path.splitext(foldname)[0]
    return '{0}_v0.meta'.format(base)

def find_method(bruker_dir):
    "returns the name of the method file"
    meths = list(Path(bruker_dir).glob('*.m/*.method'))
    if len(meths)>1:
        print('Warning, more than one method file found in',bruker_dir)
    if len(meths) == 0:
        meth = None
    else:
        meth = meths[0]
    return meth

def generate_metafile(bruker_dir, jsonfile=None):
    """
    reads a *.d Bruker FTICR dataset and generate a json file
    """
    try:
        dico = generate_dico(bruker_dir)
    except:
        print('**** Action failed on ', bruker_dir)
        dico = None

    if jsonfile is None:
        jsonfile = metaname(bruker_dir)

    if DEBUG or NO_ACTION:
        print('output file is:',jsonfile)
        print(json.dumps(dico,indent=2))

    # export to json
    if not NO_ACTION:
        if dico is not None:
            with open(jsonfile, 'w') as outfile:  
                json.dump(dico, outfile, indent=2)

def generate_dico(bruker_dir):
    """
    reads a *.d Bruker FTICR dataset and generate a dictionary
    """
    # get filenames
    from spike.File import Solarix, Apex, Apex0
    param_file = find_method(bruker_dir)

    # read all params
    if param_file is not None:
        params = Apex.read_param(str(param_file))
    elif (bruker_dir/'acqus').exists():    # Old format !
        param_file = bruker_dir/'acqus'
        oldparams = Apex0.read_param(str(param_file))
        print('OLD Parameter file format in ',bruker_dir)
        params = { }
        for k in ('EXC_hi', 'EXC_low', 'SW_h', 'TD', 'ML1', 'ML2', 'ML3', 'PULPROG'):
            params[k] = oldparams['$'+k]
        params['CLDATE'] = oldparams['$AQ_DATE'][1:-1]
        if DEBUG: print(params)
    else:
        raise Exception('No parameter found')

    # determine file type
    with open(param_file) as f: 
            lines = f.readlines()
    SpectrometerType = "Apex"
    for l in lines:
        if "solari" in l:
            SpectrometerType = "Solarix"

    # build meta data
    reduced_params = {}
    reduced_params['MetaFileType'] = "EUFTICRMS v 1.0"
    reduced_params['MetaFileVersion'] = "1.0.0"
    reduced_params['MetaFileCreationDate'] = datetime.now().isoformat()

    reduced_params['FileName'] = str(bruker_dir.name)
    reduced_params['SpectrometerType'] = SpectrometerType
    AcquisitionDate = parse(params['CLDATE'])
    reduced_params['AcqDate'] = AcquisitionDate.strftime('%Y-%m-%d')
    reduced_params['EndEmbargo'] = (AcquisitionDate + relativedelta(months=18)).strftime('%Y-%m-%d')

    reduced_params['ExcHighMass'] = params['EXC_hi']
    reduced_params['ExcLowMass'] = params['EXC_low']
    reduced_params['SpectralWidth'] = params['SW_h']
    reduced_params['AcqSize'] =  params['TD']
    reduced_params['CalibrationA'] = params['ML1']
    reduced_params['CalibrationB'] = params['ML2']
    reduced_params['CalibrationC'] = params['ML3']
    reduced_params['PulseProgam'] = params['PULPROG']

    reduced_params['MagneticB0'] = str(round(float(params['ML1'])*2*np.pi/(electron*Avogadro)*1E-3,1))
    if SpectrometerType == "Solarix":
        excfile = param_file.parent/"ExciteSweep"
        if DEBUG: print(excfile)
        if excfile.exists():
            with open(excfile,'r') as f: 
                lines = f.readlines()
            NB_step = len(lines[6:])
            reduced_params['ExcNumberSteps'] = str(NB_step)
            reduced_params['ExcSweepFirst'] = str(lines[6]).strip('\n')
            reduced_params['ExcSweepLast'] = str(lines[len(lines)-1]).strip('\n')
        else:
            reduced_params['ExcNumberSteps'] = "NotDetermined"
            reduced_params['ExcSweepFirst'] = "NotDetermined"
            reduced_params['ExcSweepLast'] = "NotDetermined"
    if DEBUG: print("Loaded parameters are:", reduced_params)
    return reduced_params

def all_files(basedir):
    "goes through all .d directories and create missing metadata files"
    count = 0
    for f in Path(basedir).glob('**/*.d'):
        metafile = metaname(f)
        if not os.path.exists(metafile):
            if DEBUG: print(f)
            generate_metafile(f, jsonfile=metafile)
            count += 1
    print ('generated %d meta files'%count)

def main():
    import argparse
    global DEBUG
    global NO_ACTION

    parser = argparse.ArgumentParser(description='Create missing FTICR metafiles.')
    parser.add_argument('base_directory', help='The base dir to be analysed')
    parser.add_argument('-n', '--no_action', action='store_true', help='prints but does not generates')
    parser.add_argument('-d', '--debug', action='store_true', help='print debugging messages')

    args = parser.parse_args()
    if args.debug:
        DEBUG = True
    if args.no_action:
        NO_ACTION = True

    all_files(args.base_directory)

if __name__ == '__main__':
    sys.exit(main())
