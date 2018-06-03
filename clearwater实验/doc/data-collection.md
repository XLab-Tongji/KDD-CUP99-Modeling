# 数据收集过程
## workload - performance data
1. generate users

    Enter cassandra node, then enter cassandra container, generate users that will be registered.
    ```
    /usr/share/clearwater/crest-prov/src/metaswitch/crest/tools/stress_provision.sh 1000
    ```
1. start workload 0.5x, 1.0x, 1.5x, 2.0x, 2.5x

    Enter stress-ng node, then enter stress-ng container, run *clearwater-sip-stress-coreonly* tool.
    ```
    # 0.5x
    /usr/share/clearwater/bin/run_stress default.svc.cluster.local \
                500 10  --initial-reg-rate 100 \
                --multiplier 225 
    # 1.0x
    /usr/share/clearwater/bin/run_stress default.svc.cluster.local \
                500 10  --initial-reg-rate 100 \
                --multiplier 450 
    # 1.5x
    /usr/share/clearwater/bin/run_stress default.svc.cluster.local \
                500 10  --initial-reg-rate 100 \
                --multiplier 675 
    # 2.0x
    /usr/share/clearwater/bin/run_stress default.svc.cluster.local \
                500 10  --initial-reg-rate 100 \
                --multiplier 900 
    # 2.5x
    /usr/share/clearwater/bin/run_stress default.svc.cluster.local \
                500 10  --initial-reg-rate 100 \
                --multiplier 1125 
    ```
1. download performace data

    See http://lab205.jios.org:12003 or download file from web interface:

    ```
    1. bono
    http://lab205.jios.org:12002/filedownload?hostId=10274&timeFrom=1527233954&timeTill=1527237815

    2. homestead
    http://lab205.jios.org:12002/filedownload?hostId=10280&TimeFrom=1527233954&timeTill=1527237815

    3. sprout
    http://lab205.jios.org:12002/filedownload?hostId=10305&TimeFrom=1527233954&timeTill=1527237815
    ```

## faultload - performance data
1. start workload at 1.0x

    Enter cassandra node, then enter cassandra container, generate users that will be registered.
    ```
    /usr/share/clearwater/crest-prov/src/metaswitch/crest/tools/stress_provision.sh 1000
    ```

    Enter stress-ng node, then enter stress-ng container, run *clearwater-sip-stress-coreonly* tool.
    ```
    /usr/share/clearwater/bin/run_stress default.svc.cluster.local \
                500 60  --initial-reg-rate 100 \
                --multiplier 450 
    ```

2. start faultload

    Enter attacker host, run *stress.py* script to begin fault load.
    ```
    ./stress.py 60
    ```

3. download performance data
   
   See described above.

1. download faultload data

    Enter attacker host, and copy */root/<date>-stress.log*

## SLA - performance data

1. start workload at 1.0x

    Enter cassandra node, then enter cassandra container, generate users that will be registered.
    ```
    /usr/share/clearwater/crest-prov/src/metaswitch/crest/tools/stress_provision.sh 1000
    ```

    Enter stress-ng node, then enter stress-ng container, run *clearwater-sip-stress-coreonly* tool.
    ```
    /usr/share/clearwater/bin/run_stress default.svc.cluster.local \
                500 60  --initial-reg-rate 100 \
                --multiplier 450 
    ```

1. start faultload 

    Enter attacker host, run *stress.py* script to begin fault load.
    ```
    ./stress.py 60
    ```

3. download performance data
   
   See described above.

1. download SLA data

    Enter stress-ng node, then enter stress-ng container, copy file /var/log/clearwater-sip-stress/<num>_caller_stats.log*