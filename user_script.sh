# script to run to install the environement in the user directory
# MAD May 2020

# first create user in group euftgrp + grplabo 
# cd to his home dir


# insure that the following code is also present in .bashrc !!!! 
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/opt/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/opt/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<


# create environment
conda create -y --use-local -n Spike numpy scipy matplotlib pytables pandas ipympl 
conda activate Spike
# and populate
# jupyter
pip --log pip.log install jupyter_contrib_nbextensions
jupyter contrib nbextension install --user
pip --log pip.log install jupytext
jupyter serverextension enable jupytext
# program
pip --log pip.log install voila spike-py

# eventuellement  Faire les tests
#python -m spike.Tests -D DATA_test

#Installer les outils locaux
fossil clone http://localhost:8070/home/casc4de/FossilRepositories/EUFT_Spike EUFT_Spike.fossil
mkdir EUFT_Spike
cd EUFT_Spike

fossil open ../EUFT_Spike.fossil
ls Easy*.py |xargs -n 1 jupytext --to notebook
rm AFAIRE.md

cd ..
# pour enlever les plugins inutiles:
EUFT_Spike/clean_plugins.sh
# créer le lien vers les données
ln -s Seadrive/My_libraries/My_Library/ FTICR_DATA

# rajouter crontab pour metafile_v0.py
