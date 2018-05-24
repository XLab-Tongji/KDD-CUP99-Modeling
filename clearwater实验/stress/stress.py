#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import time
import random
import argparse
from subprocess import Popen

hosts = [
    '192.168.1.23', # bono
    '192.168.1.26', # homestead
    '192.168.1.32', # sprout
]

inject_types = [
    'cpu',
    'mem',
    'io',
]

inject_durations = [1, 2, 3, 5]

log_file = './stress.log.tmp'
def log(host, inject_type, inject_duration):
    # get local time
    timestamp = int(time.time())
    timestamp_human = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    print (timestamp_human, timestamp, host, inject_type, inject_duration)
    with open(log_file, 'w') as file:
        file.write("%s, %s, %s, %s, %s\n" % (timestamp_human, timestamp, host, inject_type, inject_duration))


def parse_args():
    '''parse args from terminal
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("time", help="specify fault injection time (mins)", type=int)
    args = parser.parse_args()
    return args


def main():
    # parse args
    args = parse_args()
    time_expiry = args.time
    time_past = 0

    while 1:
        # choose random host
        index = random.randint(0, len(hosts)-1)
        host = hosts[index]

        # choose random inject type
        index = random.randint(0, len(inject_types)-1)
        inject_type = inject_types[index]

        # choose random inject duration
        index = random.randint(0, len(inject_durations)-1)
        inject_duration = inject_durations[index]
        time_past += inject_duration

        

        # do injection
        log(host, inject_type, inject_duration)
        if inject_type == 'none':
            time.sleep(inject_duration * 60)
        elif inject_type == 'cpu':
            cmd = "ssh root@%s stress -c 1 -t %s > /dev/null 2>&1" % (host, inject_duration * 60)
        elif inject_type == 'mem':
            cmd = "ssh root@%s stress --vm 4 --vm-bytes 1G --vm-hang %s -t %s > /dev/null 2>&1" % (host, inject_duration * 60, inject_duration * 60)
        elif inject_type == 'io':
            cmd = "ssh root@%s stress -i 100 -t %s > /dev/null 2>&1" % (host, inject_duration * 60)
            # proc = Popen(cmd)
        
        if time_past > time_expiry:
            break
        # 3min
        # time.sleep(3)

    # run after end
    os.system("mv stress.log.tmp stress-%s.log" % time.strftime("%Y-%m-%d", time.localtime()))
    print 'done...'


if __name__ == '__main__':
    main()