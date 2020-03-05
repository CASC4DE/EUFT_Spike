# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.3.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import spike
from spike.File import BrukerMS as BMS
from spike import FTICR

# %%
# ls -lh 

# %%
#data=BMS.Import_2D("ubiquitine_2D_000002.d", outfile = "ubiquitine_2D_000002.msh5")
#data.hdf5file.close()
# mais on peut aussi ne pas passer par la mémoire...

# %%
data = FTICR.FTICRData(name="ubiquitine_2D_000002.msh5",mode="onfile")

# %%
data.row(123).display()

# %%
data.axis2.sampling

# %%
# fid => spectre
data.axis2.sampling = None
data.row(123).hanning().zf(4).rfft().modulus().set_unit('m/z').display()

# %%
data.col(12345).display()
data.hdf5file.close()

# %% [markdown]
# Solarix == fichier ExciteSweep présent
#
# # je te propose
# - adapter Import2D pour les chromato - dans un 1er temps dans notebook (prototype)
#     - lire scan.xml
#         - garder tic (si présent) et peakmax
#         - garder le temps (en minute) => temps/tic (x,y)
#     - afficher chromatogram TIC / chromatogram peakmax
#     - (MAD) faire un nouvel objet TimeAxis()
#     - => manipe : 2D TimeAxis x FTICRAxis
#     - créer une manipe de chromato et la stocker
#     - faire l'importeur
#
# Ensuite
#
# - faire la FT de chaque spectre et sauver dans un autre msh5
#     - downsampling
#     - compression
# - outils pour afficher le chromagram
#     - tic
#     - spectre total (sum(peak d'un spectre))
#     - chromatogram pour un range de m/z
#     - spectre m/z pour un range de temps du chromatogram
#     

# %%
from xml.etree import cElementTree as ET

f = open("BSA/scan.xml", "r")
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

import matplotlib.pyplot as plt
plt.plot(minutes_list, tic_list)
plt.show()


# %%
len(tic_list)

# %%
import os
import numpy as np
from spike.FTICR import FTICRData
from spike.File import Solarix, Apex
from spike.NPKData import TimeAxis


# %%
# ls -lh 

# %% [markdown]
# ### import 2D
# - le mode outfile ne charge pas en mémoire
# - le mode onfile mets les données en "memory mapping"

# %%
if not os.path.exists('BSA.msh5'):
    d = Apex.Import_2D('BSA', outfile='BSA.msh5')
else:
    d = FTICRData(name='BSA.msh5', mode='onfile')
d

# %% [markdown]
# ### passer en chromato => va devenir Import_chromato..

# %%
d.axis1 = TimeAxis(size=d.size1, tabval=np.array(minutes_list)*60, currentunit='min' )
d.axis2.sampling = None # - je crois que j'ai corrigé le bug - mais pas sûr !
d

# %% [markdown]
# ### processing simple d'un fid

# %%
d.row(123).hanning().zf(4).rfft().modulus().set_unit('m/z').display(zoom=(148,1300));

# %%
d.axis2.sampling is None

# %%
final_size = d.row(123).hanning().zf(4).rfft().modulus().set_unit('m/z').size1
final_size
d.hdf5file.close()

# %% [markdown]
# # pour Camille
# ### `importandcompute_LCMS.py`
# - créer un msh5 vide de   d.size1 x final_size - mode compressé (s'insipirer de processing.py)
#     - avec un axis1 en temps
#     - avec axis2 FTICR
# - for "toute exp dans le ser"  (s'inspirer de l'importeur 2D)
#     - extraire le fid
#     - process
#     - thresholding à n x sigma
#     - stocker dans le spectre dans le msh5
# - stocker les annexes (tic - maxpeaks)
# - calculer le downsampling (reprendre de processing.py)
#
#
#
# à terme il faudrait faire un module avec tout ça et l'utiliser dans processing comme dans `import_n_compute`
#  

# %%
from spike.File.HDF5File import HDF5File
hfar =  HDF5File("ubiquitine_2D_000002.msh5", "w") #, debug=debug)  # OUTFILE for all resolutions

# %%
d1 = FTICRData( dim = 2 )   # create dummy 2D
d1.axis1 = TimeAxis(size=d1.size1, tabval=np.array(minutes_list)*60, currentunit='min' )
#d1.axis2.size = d1.   # taille d'un fid (512k)
#d1.axis1.size = sizeF1   # longeur de la LC (4k)

group = 'resol1'
#if param.compress_outfile:    # file is compressed
hfar.set_compression(True)
hfar.create_from_template(d1, group)

#=> 
#for i in range(d1.size1):
#    d.row(i).hanning().zf(4).rfft().modulus()
#    d1.set_row(i, d)

#    ...
hfar.hdf5file.close()    

# %% [markdown]
# # pour MAD
# - ✅ bug de sampling -
# - ✅ bug de Bo
# - rajouté importunit dans TimeAxis - car les chromato sont presque toujours en minutes !
#
# Il faut recharcher SPIKE depuis bitbucket - revision 460 minimum
#
# À faire:
# - il faudra rajouter les temps en unix TU  !
# - PALMA not loaded !
# - d.axis2.sampling = b'None'

# %%
eval('None')

# %%
