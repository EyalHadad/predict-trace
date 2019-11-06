from multiprocessing import Pool, Manager
from subprocess import Popen
import time
import csv
import sys
import os
from tempfile import mktemp


def run_process(cmd_args):
    print "Running", cmd_args
    proc = Popen(cmd_args)
    proc.communicate()


def main(num_processes, cmd_lines_path):
    p = Pool(int(num_processes))
    with open(cmd_lines_path) as f:
        p.map(run_process, csv.reader(f))


def main_cmds(num_processes, cmds):
    file_name = mktemp()
    with open(file_name, 'wb') as f:
        csv.writer(f).writerows(cmds)
    main(num_processes, file_name)
    os.remove(file_name)


if __name__ == '__main__':
    main(*sys.argv[1:])

""" Running example:
python test_process.py 3 process.csv
process.csv:
python,-c,import time;time.sleep(10);print 100
python,-c,import time;time.sleep(10);print 100
python,-c,import time;time.sleep(10);print 100
python,-c,import time;time.sleep(10);print 100
python,-c,import time;time.sleep(10);print 100
python,-c,import time;time.sleep(10);print 100
python,-c,import time;time.sleep(10);print 100
python,-c,import time;time.sleep(10);print 100
python,-c,import time;time.sleep(10);print 100
python,-c,import time;time.sleep(10);print 100
"""