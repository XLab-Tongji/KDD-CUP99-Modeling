# 数据收集过程
## start workload
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

## start faultload
Enter attacker host, run *stress.py* script to begin fault load.
```
./stress.py 60
```

## download performance data
See http://lab205.jios.org:12003

OR download file from web interface:

```
1. bono
http://lab205.jios.org:12002/filedownload?hostId=10274&timeFrom=1527233954&timeTill=1527237815

2. homestead
http://lab205.jios.org:12002/filedownload?hostId=10280&TimeFrom=1527233954&timeTill=1527237815

3. sprout
http://lab205.jios.org:12002/filedownload?hostId=10305&TimeFrom=1527233954&timeTill=1527237815
```
