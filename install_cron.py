'''
prgm to install needed crontab lines for each account
generates a weekly week_meta0.log
and a montly month_meta0.log

One action every 10 min to scan the folder
one action every week to clean the log
located at the "anniversary minute" the cron was installed
'''
import time
from subprocess import run


print('installing cron', end='...')

# compute minute
i = time.localtime().tm_min % 10
#print(i,end=': ')
ll = [str(j) for j in range(i,60,10)]
ltime = ",".join(ll)

# commands
cmd = "/opt/anaconda3/bin/python EUFT_Spike/metafile_v0.py FTICR_DATA"
out = "week_meta0.log"
out2 = "month_meta0.log"
cronline0 =  "# 3 Lines added by the EUFT_Spike project\n"
cronline1 = ("%s * * * * %s >> %s 2>&1\n"%(ltime, cmd, out))   # every ten minutes
cronline2 = ("%d 5 * * 0 rm %s >> %s 2>&1\n"%(i, out, out2))   # every sunday morning at 5

# get existing cron
ntry = 1
cron = run('crontab -l', shell=True, capture_output=True) 

# chek if it went wrong - could be because crontab is not initialized
while cron.returncode != 0:
    print('\nproblems in crontab')
    print(cron.stdout.decode())
    print(cron.stderr.decode())
    if "no crontab" in cron.stderr.decode():   # maybe just cron not initialized !
        print('intializing crontab...')
        ntry += 1
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

alreadypresent = "EUFT_Spike" in table
if alreadypresent:
    print("\nremoving previous entry")
    lines = table.split("\n")
    new_table = []
    for il,line in enumerate(lines):  # skip first lines
        if "EUFT_Spike" not in line:
            new_table.append(line)
        else:
            break
    if "EUFT_Spike" in line:
        values = line.split(' ')
        try:
            nlines = int(values[1])
        except:
            print('Error in processing crontab - Abort')
            exit(2)
    for line in lines[il+nlines:]:
        new_table.append(line)
    table = "\n".join(new_table)

# create the table
table += cronline0 + cronline1 + cronline2
# print('--')
# print(table)
cron = run('crontab -', shell=True, input=table, text=True, capture_output=True)
if cron.returncode != 0:
    print('\nproblems in crontab')
    print(cron.stdout.decode())
    print(cron.stderr.decode())
    print('Please check crontab manually It should contain:')
    print(table)
else:
    print('Done.')

