# prints version level when run as a module: python -m EUFT_Spike
import spike
from .Tools import FTICR_INTER as FI

print(    '''
##############################
    EU-FTICR-MS Interface
         by CASC4DE
##############################
   Current Version
 - spike version: %s
 - interface version: %s
##############################
'''%(spike.version.version, FI.version))