# script to run to install the environement in the user directory
# MAD May 2020

# see update.sh  for updating an existing account

# first create user (je crois que j'ai les bonnes commandes)
# user new_user - in group newlab and euftgrp

# >> sudo addgroup newlab (par exemple)
# >> sudo adduser new_user --ingroup newlab
# >> sudo adduser new_user euftgrp

# cd to his home dir
# sudo su new_user
# then execute this script 

version="1.02"
echo "EUFT Installation - version $version"
# init of conda
/opt/anaconda3/condabin/conda init
source .bashrc

# create environment
# conda create -y --use-local -n Spike numpy scipy matplotlib pytables pandas ipympl 
# conda activate Spike
conda install --use-local -y numpy scipy matplotlib pytables pandas ipympl

# and populate
# jupyter
pip --log pip.log install --user jupyter_contrib_nbextensions

echo '# >> jupyter nbextension' >> .bashrc
echo 'export PATH="'$HOME'/.local/bin:$PATH"' >> .bashrc
echo '# << jupyter nbextension' >> .bashrc
source .bashrc

jupyter contrib nbextension install --user
pip --log pip.log install --user jupytext
jupyter serverextension enable jupytext

# program
pip --log pip.log install --user voila
pip --log pip.log install --user -U spike-py

# eventuellement  Faire les tests
#python -m spike.Tests -D DATA_test

# Installer les outils locaux
fossil clone http://localhost:8070/home/casc4de/FossilRepositories/EUFT_Spike EUFT_Spike.fossil
mkdir -p EUFT_Spike
cd EUFT_Spike
fossil open ../EUFT_Spike.fossil
rm AFAIRE.md

ls Easy*.py |xargs -n 1 jupytext --to notebook

# and move to $HOME
mv EasyDisplayLCFTICR.ipynb    ../LCMS_Tool.ipynb
mv EasyProcessFTICR-MS.ipynb  ../Process_Tool.ipynb

cd ..

# pour enlever les plugins inutiles:
EUFT_Spike/clean_plugins.sh

# créer le lien vers les données
if [ -f "FTICR_DATA" ] ; then
    echo "FTICR_DATA present"
else
    ln -s SeaDrive/ FTICR_DATA
fi

# pour les taches automatiques
pip --log pip.log install --user doit

# "=== update crontab"
python EUFT_Spike/install_cron.py

# then show version numbers

echo "=== Done"
python -m EUFT_Spike 

