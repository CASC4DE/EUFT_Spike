# 2D FTICR-MS processing in the EU-FTICR-MS project
This is an example job folder to be handled by QM (see http://github.com/delsuc/QM ).
Two files are required

- proc_config.cfg : the configuration file - both for QM and for processing
- LaunchEUFTICR.py : the program itself

The program is meant to run as root, it first copies files to the working dir 
(  `/tmp/usename/processing` ) then launch in there mpirun with the given nb of proc
and running the processing4EU.py program. typically `/home/username/EUFT_Spike/processing4EU.py` .

Then it copies the created files back to the original directory, but as user_id for preserving accesses.
 
