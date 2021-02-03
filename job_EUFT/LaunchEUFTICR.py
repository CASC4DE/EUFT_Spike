#!/usr/bin/env python
# encoding: utf-8
"""
Launch a process under an other id - used for EUFTICR projects
"""

import os, sys
import pwd
import shutil
import subprocess
import glob
from pathlib import Path  # better than os.path
from configparser import ConfigParser

DEBUG = True     # print additional messages
DONT = True     # do nothing 

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

def user_mail(username):
    "find user mail from username"
    user_path = Path('/home')/username
    user_mail = 'unknown'
    with open(user_path/"seadrive.conf") as f:
        for line in f:
            if line.startswith("username"):
                split_line = line.split("=")
                user_mail = split_line[1].strip(' ').strip('\n')
                break
    return user_mail

def user_SeaDrive_path(username):
    "find seadrive_path from username"
    seadrive_path = Path("/mnt/iscsi-FTICR-DATA/fuse-data/")/user_mail(username)
    for base, dirs, files in os.walk(seadrive_path):
        for d in dirs:
            if d.endswith("My Library"):
                user_seaDrive_path = seadrive_path/d
    return user_seaDrive_path

def locate_acquisition(folder):
    """
        From the given folder this function return the absolute path to the apexAcquisition.method file
        It should always be in a subfolder 
        ( copied from spike.File.Solarix )
    """
    L = glob.glob(os.path.join(folder,"*","apexAcquisition.method"))
    if len(L)>1:
        raise Exception( "You have more than 1 apexAcquisition.method file in the %s folder, using the first one"%folder )
    elif len(L) == 0: 
        raise Exception( "You don't have any apexAcquisition.method file in the  %s folder, please double check the path"%folder )
    return Path(L[0])

def LaunchEUFTICR(config):
    """
    reads the configuration, launch the processing, and copy back to the userdir the processed files
    """
    usermail  = config.get('QMOptions', "e_mail")
    nproc     = config.get('QMOptions', "nb_proc")
    username  = config.get('Proc', "username")
    directory = config.get('Proc', "directory")
    mscffile  = config.get('Proc', "mscf_file")

    # determine origin dir
#    seadrive_path = Path("/mnt/iscsi-FTICR-DATA/fuse-data/")/user_mail_from_name(username)
    fromdir = user_SeaDrive_path(username)/'FTICR_DATA'/directory
    if DEBUG:
        print('fromdir', fromdir)
    # we'll work in a tmp dir
    workdir = Path('/tmp')/username/directory
    workdir.mkdir(mode=0o777, parents=True, exist_ok=True)  # create
    if DEBUG:
        print('workdir', workdir)
    methdir = locate_acquisition(fromdir).parent
    # copy *.m methods dir
    shutil.copytree(methdir, workdir/'methods.m')
    # copy needed files
    list_of_files = ['ser', 'scan.xml', mscffile]
    for f in list_of_files:
        shutil.copy(fromdir/f, workdir/f)
    #    cd to tmpdir
    os.chdir(workdir)
    # determine output filename
    jobconfig = ConfigParser()
    jobconfig.read(mscffile)
    outfile = jobconfig.get('processing','outfile')
    # and launch
    errorlog = open('error.log','w')
    outputlog = open('output.log','w')
#    cmd = 'echo mpirun -nb {0} python process4EU.py {1}'.format(nproc, mscffile)
#    subprocess.run(cmd, shell=True, stdout=outputlog, stderr=errorlog)
    cmdl = ['mpirun', '-nb', nproc, 'python', 'process4EU.py', mscffile]
    if DONT:
        cmdl = ['echo']+cmdl
    subprocess.run(cmdl, shell=False, stdout=outputlog, stderr=errorlog)
    outputlog.close()
    errorlog.close()
    # copy back processed files + logs
    list_of_files = [str(f) for f in Path('.').glob("*.log")]
    list_of_files.append(outfile)
    if DONT:
        subprocess.run(['touch', outfile], shell=False)
    if DEBUG:
        print('copy back:', list_of_files)
    for f in list_of_files:
        shutil.chown(f, user=username, group=username)
#        os.chmod(l, 0o666)
#    user_path = os.path.join('/home',str(username))
    user_uid = pwd.getpwnam(str(username)).pw_uid
    user_gid = pwd.getpwnam(str(username)).pw_gid

    fromuser = Path('/home')/username/"FTICR_DATA"/"My Library"/"FTICR_DATA"
    cmdl = ['cp'] + list_of_files + [str(fromuser)]
    if DONT:
        cmdl = ['echo']+cmdl
    if DEBUG:
        print(cmdl)
#    subprocess.run(cmdl, shell=False)
    cp_pid = subprocess.Popen(cmdl, preexec_fn=demote(user_uid, user_gid)).pid

#    rmdir tmpdir
    if DONT:
        print('to remove:', workdir)
    else:
        shutil.rmtree(workdir)

"""
#improvements

## changer en rsync
    for f in list_of_files:
        shutil.copy(fromdir/f, workdir/f)

## 
"""
"""ligne 785 de Welcome/view
        #change file permissions, owners to permit a cp in the user folder
        shutil.chown(tmp_save_file_path, user=username, group=username)
        os.chmod(tmp_save_file_path, 0o777)
        user_path = os.path.join('/home',str(username))
        user_uid = pwd.getpwnam(str(username)).pw_uid
        user_gid = pwd.getpwnam(str(username)).pw_gid
        print("This is user_uid:",user_uid)
        print("This is user_gid:",user_gid) 
        if not os.path.exists(user_path):
            os.makedirs(user_path, mode     config = ConfigParser()
    config.read(configfile)
= 0o777)
        user_fticr_path = os.path.join(user_path,"FTICR_DATA","My\ Library")
        SaveFilePath = os.path.join(user_fticr_path,project_spath)
        cmd = ['cp {0} {1}'.format(tmp_save_file_path, SaveFilePath)]
        cp_pid = subprocess.Popen(cmd, shell=True, executable='/bin/bash', cwd=user_path, preexec_fn=demote(user_uid, user_gid)).pid
        # allow user to download it
        return send_from_directory(directory=dirs_to_create, filename=save_file_name, as_attachment=True) # and redirect(url_for('user',username=current_user.username))
"""

if __name__ == "__main__":
    configfile = sys.argv[1]
    config = ConfigParser()
    config.read(configfile)
    processing = LaunchEUFTICR(config)
