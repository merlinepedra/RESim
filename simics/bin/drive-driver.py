#!/usr/bin/env python3
'''
Send data files to the driver and from there, send them to one or more target IP/ports.
Executes magic instruction 99 just prior to sending data to reset RESim origin.
'''
import os
import time
import socket
import sys
import subprocess
import argparse
import shlex
resim_dir = os.getenv('RESIM_DIR')
core_path=os.path.join(resim_dir,'simics', 'monitorCore')
sys.path.append(core_path)
import runAFL
import resimUtils
def main():
    parser = argparse.ArgumentParser(prog='drive-driver.py', description='Send files to the driver and from there to one or more targets.')
    parser.add_argument('directives', action='store', help='File containing driver directives')
    parser.add_argument('-n', '--no_magic', action='store_true', help='Do not execute magic instruction.')
    parser.add_argument('-t', '--tcp', action='store_true', help='Use TCP.')
    args = parser.parse_args()
    print('Drive driver')
    if not os.path.isfile(args.directives):
        print('No file found at %s' % args.directives)
        exit(1)
    if args.tcp:
        client_cmd = 'clientTCP'
    else:
        client_cmd = 'clientudpMult'
    client_mult_path = os.path.join(core_path, client_cmd)

    cmd = 'scp -P 4022 %s  mike@localhost:/tmp/' % client_mult_path
    result = -1
    count = 0
    while result != 0:
        result = os.system(cmd)
        #print('result is %s' % result)
        if result != 0:
            print('scp of %s failed, wait a bit' % client_mult_path)
            time.sleep(3)
            count += 1
            if count > 10:
                print('Time out, more than 10 failures trying to scp to driver.')
                sys.exit(1)
    exit
    magic_path = os.path.join(resim_dir, 'simics', 'magic', 'simics-magic')
    cmd = 'scp -P 4022 %s  mike@localhost:/tmp/' % magic_path
    os.system(cmd)

    remote_directives_file = '/tmp/directives.sh'
    driver_file = open(remote_directives_file, 'w')
    driver_file.write('sleep 2\n')
    if not args.no_magic:
        driver_file.write('/tmp/simics-magic\n')
    with open(args.directives) as fh:
        for line in fh:
            if line.strip().startswith('#'):
                continue
            if len(line.strip()) == 0:
                continue
            parts = line.split()
            if len(parts) == 2 and parts[0] == 'sleep':
                driver_file.write(line)
            if args.tcp and len(parts) != 3:
                print('Invalid TCP driver directive: %s' % line)
                print('    iofile ip port')
                exit(1)
            elif not args.tcp and len(parts) != 4:
                print('Invalid driver directive: %s' % line)
                print('    iofile ip port header')
                exit(1)
            else:
                iofile = parts[0]
                ip = parts[1]
                port = parts[2]
                if not args.tcp:
                    header = parts[3]
                else:
                    header = ''
                base = os.path.basename(iofile)
                directive = '/tmp/%s  %s %s %s /tmp/%s' % (client_cmd, ip, port, header, base)
                driver_file.write(directive+'\n')
                cmd = 'scp -P 4022 %s  mike@localhost:/tmp/' % iofile
                os.system(cmd)

    driver_file.close()

    cmd = 'chmod a+x %s' % remote_directives_file
    os.system(cmd)

    cmd = 'scp -P 4022 %s  mike@localhost:/tmp/' % remote_directives_file
    os.system(cmd)
    cmd = 'ssh -p 4022 mike@localhost "nohup %s > /dev/null 2>&1 &"' % remote_directives_file
    os.system(cmd)

if __name__ == '__main__':
    sys.exit(main())
