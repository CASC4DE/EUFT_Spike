# update of 15 May 2020
# clean
find $HOME -path '*.pyc' -delete
mkdir -p prev_ipynb
mv *.ipynb prev_ipynb

# update
# spike
pip --log pip.log install --user -U spike-py
# EU tools
cd EUFT_Spike
fossil revert
fossil update
ls Easy*.py |xargs -n 1 jupytext --to notebook

# and move to $HOME
mv EasyDisplayLCFTICR.ipynb    ../LCMS_Tool.ipynb
mv EasyProcessFTICR-MS.ipynb  ../Process_Tool.ipynb

cd ..
