#!/usr/bin/env python

# caller_stats.log
# 2 CurrentTime
# 10 OutgoingCall(P)
# 16 FailedCall(P)

info_list = []
with open('sla.log', 'r') as file:
    lines = file.readlines()
    for line in lines:
        elements = line.split(';')
        info_list.append((elements[2], elements[10], elements[16]))
        
info_list = info_list[2:-1]
for info in info_list:
    if info[1] == '0':
        continue
    print info[0].split('\t')[1].split('.')[0], 'Fail: %0.2f%%' % (float(info[2]) / float(info[1]) * 100)
