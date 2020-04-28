#!/usr/bin/env python
# coding: utf-8
-*- coding: utf-8 -*-
"""
This programs goes throught a directory tree and adds a _vo metafile to the data-set lacking one
"""

import os
import numpy as np
import spike
from spike.File import Solarix, Apex
from scipy.constants import N_A as Avogadro
from scipy.constants import e as electron
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime
from pathlib import Path


# +
DEBUG = False

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
    dico = generate_dico(bruker_dir)

    if jsonfile is None:
        jsonfile = metaname(bruker_dir)

    if DEBUG:
        print('output file is:',jsonfile)

    # export to json
    with open(jsonfile, 'w') as outfile:  
        json.dump(dico, outfile, indent=2)


# -

def generate_dico(bruker_dir):
    """
    reads a *.d Bruker FTICR dataset and generate a dictionary
    """
    # get filenames
    param_file = find_method(bruker_dir)

    # read all params
    params = Apex.read_param(str(param_file))

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
    reduced_params['CalibrationB'] = params['ML1']
    reduced_params['CalibrationC'] = params['ML1']
    reduced_params['PulseProgam'] = params['PULPROG']

    reduced_params['MagneticB0'] = str(round(float(params['ML1'])*2*np.pi/(electron*Avogadro)*1E-3,1))
    if SpectrometerType == "Solarix":
        with open(os.path.join(os.path.dirname(param_file),"ExciteSweep")) as f: 
            lines = f.readlines()
        NB_step = len(lines[6:])
        reduced_params['ExcNumberSteps'] = str(NB_step)
        reduced_params['ExcSweepFirst'] = str(lines[6]).strip('\n')
        reduced_params['ExcSweepLast'] = str(lines[len(lines)-1]).strip('\n')
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


all_files('/DATA/DATA/FT-ICR/M.Witt/Data for Marc Andre Delsuc April 2019/Ubiquitin')

BD = "/DATA/DATA/FT-ICR/M.Witt/Data for Marc Andre Delsuc April 2019/Ubiquitin/Ubiquitin CID_000001.d"
metaname(BD), Path(BD).name

list(Path(BD).glob('*.m/*.method'))

Path(BD).parent

os.path.splitext(BD)


