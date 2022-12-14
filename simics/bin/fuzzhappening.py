#!/usr/bin/env python
#
# given a an AFL session named by target, compare all of the coverage
# files and de-dupe them, creating a list of the smallest queue files
# generate unique a set of hits.
#
import sys
import os
import glob
import shlex
import argparse
import subprocess
try:
    import ConfigParser
except:
    import configparser as ConfigParser
resim_dir = os.getenv('RESIM_DIR')

sys.path.append(os.path.join(resim_dir, 'simics', 'monitorCore'))
import aflPath

def main():
    afldir = os.getenv('AFL_DIR')
    wu = os.path.join(afldir, 'afl-whatsup')
    parser = argparse.ArgumentParser(prog='fuzzhappening', description='Show fuzzing status of sync dirs')
    #parser.add_argument('target', action='store', help='The AFL target, generally the name of the workspace.')
    args = parser.parse_args()
    here=os.getcwd()
    base=os.path.basename(here)
    sync_dir = aflPath.getTargetPath(base)
    cmd = '%s -s %s' % (wu, sync_dir)
    whatsup = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output = whatsup.communicate()
    for line in output[1].decode("utf-8").splitlines():
         print(line)
    for line in output[0].decode("utf-8").splitlines():
         print(line)

if __name__ == '__main__':
    sys.exit(main())
