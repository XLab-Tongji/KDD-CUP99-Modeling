#!/usr/bin/env bash
# 系统扰动脚本

# # test
# TIMEOUT=10
# SLEEP_TIMEOUT=10s

TIMEOUT=300
SLEEP_TIMEOUT=5m

hostname=$(hostname)
LOG_FILE="./${hostname}_stress.log"

INJECT_CPU="stress -c 1 -t ${TIMEOUT}"
INJECT_MEM="stress --vm 4 --vm-bytes 1G --vm-hang ${TIMEOUT} -t ${TIMEOUT}"
INJECT_IO="stress -i 100 -t ${TIMEOUT}"

time=0
function timestamp() {
    time=$(date +%s)
    end=$[$time % 10]

    targetTime=0
    if [ $end -gt 5 ]; then
        targetTime=$[time - end + 5]
    else
        targetTime=$[time - end]
    fi
    time=$targetTime
}

function log() {
    stage=$1
    type=$2
    flag=$3

    timestamp
    echo "${stage} ${flag} ${type} ${time} ${hostname} $(date +%T)" 
    echo "${stage} ${flag} ${type} ${time} ${hostname} $(date +%T)" >> ${LOG_FILE}
}

echo 'start 1 -> 14'
echo 'start 1 -> 14' > ${LOG_FILE}
# 无扰动运行
log 1 "normal" "start" 
sleep ${SLEEP_TIMEOUT}
log 1 "normal" "stop" 

# CPU扰动
log 2 "cpu" "start"
${INJECT_CPU} > /dev/null 2>&1
log 2 "cpu" "stop"

# 无扰动运行
log 3 "normal" "start"
sleep ${SLEEP_TIMEOUT}
log 3 "normal" "stop"

# MEM扰动
log 4 "mem" "start"
${INJECT_MEM} > /dev/null 2>&1
log 4 "mem" "stop"

# 无扰动运行
log 5 "normal" "start"
sleep ${SLEEP_TIMEOUT}
log 5 "normal" "stop"

# IO扰动
log 6 "io" "start"
${INJECT_IO} > /dev/null 2>&1
log 6 "io" "stop"

# 无扰动运行
log 7 "normal" "start"
sleep ${SLEEP_TIMEOUT}
log 7 "normal" "stop"

echo 'end 1 -> 14'
echo 'end 1 -> 14' >> ${LOG_FILE}
