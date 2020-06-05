# update of a user account already installed

echo update of 5 june 2020

echo "=== cleaning previous stuff"
find $HOME -path '*.pyc' -delete
mkdir -p prev_ipynb
mv *.ipynb prev_ipynb

# update
# spike
echo "=== update spike"
pip --log pip.log install --user -U spike-py
# EU tools
echo "=== update EU tools"
cd EUFT_Spike
fossil revert
fossil update
cp import_default.mscf C4template/static/
ls Easy*.py |xargs -n 1 jupytext --to notebook

# and move to $HOME
mv EasyDisplayLCFTICR.ipynb    ../LCMS_Tool.ipynb
mv EasyProcessFTICR-MS.ipynb  ../Process_Tool.ipynb

cd ..
# pour enlever les plugins inutiles:
EUFT_Spike/clean_plugins.sh

# install crontab
#echo "=== update crontab"
#python EUFT_Spike/install_cron.py

# then show version numbers

echo "=== Done"
python -m EUFT_Spike 
