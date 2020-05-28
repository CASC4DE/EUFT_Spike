#!/usr/bin/env python 
# encoding: utf-8
"""
doit command file to process LCMS and 2DMS files which requires lengthy processing

Processing is conditioned to the presence of a correctly named mscf file
    - import***.mscf for LCMS
    - process***.mscf for 2DMS

a new processing will be lauched if the mscf is new or have changed.

additional doc on doit : https://pydoit.org/contents.html
"""

from __future__ import print_function
from pathlib import Path
from pprint import pprint
#import configparser
import ImportLCmp as Import
#import processing_4EU as proc2D

BASE = 'FTICR_DATA' #'/media/mad/extfat/DATA/FT-ICR' #'/DATA' #'FTICR_DATA' 
version = "1.0.0"

##### CONFIGURATION ############
DEBUG = False

DOIT_CONFIG = {
    # backend of db in json, for easier debugging
    'backend': 'json',
    'dep_file': 'doit-db.json',
    # any change in the date will trigger execution - more greedy, but faster than MD5.
    'check_file_uptodate': 'timestamp',
    # output from actions should be sent to the terminal/console
    'verbosity': 1,
    # does not stop execution on first task failure
    'continue': True,
    # doit should only report on executed actions
    # 'reporter': 'executed-only',
    # use multi-processing / parallel execution
    'num_process': 1,
}
if not DEBUG:
    DOIT_CONFIG['reporter'] = 'executed-only'
    DOIT_CONFIG['verbosity'] = 2
else:
    DOIT_CONFIG['reporter'] = 'executed-only' #'json'


######## Tools ##############################
def get_2Dtodo(loc=BASE):
    """
    returns the list of 2D to be processed 
    A 2D is to be processed if a processing*.mscf file appears in the .d folder
    returns the list of *.mscf files
    """
    toproc = []
    for ff in Path(loc).glob("**/*.d/proces*.mscf"):
        if (ff.parent/'ser').exists():
            toproc.append(ff)
    if DEBUG:
        print('get_2Dtodo:')
        pprint([str(i.parent.name) for i in toproc])
    return toproc

def get_LCtodo(loc=BASE):
    """
    returns the list of LC to be processed 
    A LC is to be processed if a import*.mscf file appears in the .d folder
    returns the list of *.mscf files
    """
    toproc = []
    for ff in Path(loc).glob("**/*.d/import*.mscf"):
        if (ff.parent/'ser').exists():
            toproc.append(ff)
    if DEBUG: 
        print('get_LCtodo')
        pprint([str(i.parent.name) for i in toproc])
    return toproc

############## Tasks #######################
def _task_2Dprocess():
    "process 2D experiment from the processing*.mscf files"
    for ff in get_2Dtodo():
        config = Import.Proc_Parameters(ff)
        name = "2D_"+ff.parent.name
        ser = ff.parent/'ser'
        outname = config.outfile
        action = "python processing.py %s"%(ff)
        if DEBUG:
            action = "echo "+action
        ans = {
            'name': name,  # name required to identify tasks
            'file_dep': [ser],  # file dependency
            'targets': [outname],
            # In case there is no modification in the dependencies and the targets already exist, it skips the task.
            # If a target doesn’t exist the task will be executed.
            'actions': [action]
        }
        if DEBUG:
            print("TASK:")
            pprint(ans)
        yield ans

def task_LCprocess():
    "process LC experiment from the import*.mscf files"
    for ff in get_LCtodo():
        config = Import.Proc_Parameters(ff)
        name = str(ff)
        ser = ff.parent/'ser'
        outname = config.fulloutname
        #if DEBUG: print (config.report())
        action = ["python", "EUFT_Spike/ImportLCmp.py", "-d", ff]
        if DEBUG:
            action = ["echo"]+action
        ans = {
            'name': outname,  # name required to identify tasks
            'file_dep': [ser, ff],  # file dependency
            'targets': [outname],
            # In case there is no modification in the dependencies and the targets already exist, it skips the task.
            # If a target doesn’t exist the task will be executed.
            'actions': [action]
        }
        # if DEBUG:
        #     print("TASK:")
        #     pprint(ans)
        yield ans

