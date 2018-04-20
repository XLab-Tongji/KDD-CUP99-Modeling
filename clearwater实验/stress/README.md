
# 压测
# 进入node24
docker exec -it $(docker ps |grep clearwater-cassandra |awk {'print $1'}) bash
    
/usr/share/clearwater/crest-prov/src/metaswitch/crest/tools/stress_provision.sh 33000

# 进入node32
apt-get update
apt-get install clearwater-sip-stress-coreonly -y

docker exec -it $(docker ps |grep clearwater-sprout |awk {'print $1'} | head -1) bash

/usr/share/clearwater/bin/run_stress default.svc.cluster.local \
            400 5  --initial-reg-rate 100 \
            --icscf-target 10.42.37.74:5052 \
            --scscf-target 10.42.37.74:5054

/usr/share/clearwater/bin/run_stress default.svc.cluster.local \
            1000 5  --initial-reg-rate 100 \
            --icscf-target 10.42.37.74:5052 \
            --scscf-target 10.42.37.74:5054

/usr/share/clearwater/bin/run_stress default.svc.cluster.local \
            30000 105  --initial-reg-rate 100 \
            --icscf-target 10.42.37.74:5052 \
            --scscf-target 10.42.37.74:5054
    
docker exec -it $(docker ps |grep clearwater-cassandra |awk {'print $1'} | head -1) bash

