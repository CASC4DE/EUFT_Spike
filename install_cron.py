# prgm to install needed crontab lines for each account
import time
from subprocess import run

# One action every 10 min to scan the folder
# one action every week to clean the log
# located at the "anniversary minute" the cron was installed

print('installing cron', end='...')

# compute minute
i = time.localtime().tm_min % 10
#print(i,end=': ')
ll = [str(j) for j in range(i,60,10)]
ltime = ",".join(ll)

# commands
cmd = "/opt/anaconda3/bin/python EUFT_Spike/metafile_v0.py FTICR_DATA"
out = "meta0.log"
out2 = "cleanmeta0.log"
cronline0 =  "# 3 Lines added by the EUFT_Spike project\n"
cronline1 = ("%s * * * * %s >> %s 2>&1\n"%(ltime, cmd, out))   # every ten minutes
cronline2 = ("%d 5 * * 0 rm %s >> %s 2>&1\n"%(i, out, out2))   # every sunday morning at 5

# get existing cron
ntry = 1
cron = run('crontab -l', shell=True, capture_output=True) 

# chek if it wen wrong - could be because crontab is not initialized
while cron.returncode != 0:
    print('\nproblems in crontab')
    print(cron.stdout.decode())
    print(cron.stderr.decode())
    if "no crontab" in cron.stderr.decode():   # maybe just cron not initialized !
        print('intializing crontab...')
        ntry =+ 1
        cron = run("echo '# intializing crontab.\n' |crontab -", shell=True, capture_output=True) 
        if cron.returncode != 0:
            print('Failed')
            exit(1)
        #cron = run("echo '#\n'", shell=True, capture_output=True) 
        time.sleep(1)
        cron = run('crontab -l', shell=True, capture_output=True) 
    if ntry > 3:
        print('Abort')
        exit(1)

table = cron.stdout.decode()
alreadydone = "EUFT_Spike" in table
if alreadydone:
    print("Nothing to do.")
else:                             # create the table
    table += cronline0 + cronline1 + cronline2
#    run('cat - > toto.test', shell=True, input=table, text=True)
    run('crontab -', shell=True, input=table, text=True)
    print('Done.')

