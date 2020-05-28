import pwd, grp, os, time
from pathlib import Path
import subprocess

"""
This code goes through all ueftgroup users and execute a command 
in their account, with their id.
"""

def demote(user_uid, user_gid):
    """
    Pass the function 'set_ids' to preexec_fn, rather than just calling
    setuid and setgid. This will change the ids for that subprocess only
    From: https://gist.github.com/sweenzor/1685717
    """
    def set_ids():
        os.setgid(user_gid)
        os.setuid(user_uid)
    return set_ids

def run_id(direc, cmd, user_name):
    "cd to direc and execute cmd as user_name"
    user_uid = pwd.getpwnam(user_name).pw_uid
    user_gid = pwd.getpwnam(user_name).pw_gid
    os.chdir(direc)
    pid = subprocess.Popen(cmd, shell=True, preexec_fn=demote(user_uid, user_gid))

def for_all_grp(cmd='ls -lh', grptodo='euftgrp'):
    gr_euft = grp.getgrnam(grptodo)
    for user_name in gr_euft.gr_mem:
        user_path = pwd.getpwnam(user_name).pw_dir    # Path('/home')/user_name
        print('#############################\n',user_name, user_path)
        run_id(user_path, cmd, user_name)
        time.sleep(2)

if __name__ == '__main__':
#    cmd = 'ls -lh FTICR_DATA/*'
    cmd = '/opt/anaconda3/bin/python -m doit -f EUFT_Spike/dodo.py -d . >> dodo.log'
    for_all_grp(cmd)
