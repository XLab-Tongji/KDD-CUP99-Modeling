# 批量ssh信任注册
for i in 22 23 24 25 26 27 28 29 30 31 32
do
    ssh-copy-id root@192.168.1.${i} -f
done

# 批量安装stress工具
for i in 22 23 24 25 26 27 28 29 30 31 32
do
    ssh root@192.168.1.${i} 'apt-get install stress > /dev/null'
done

# 拷贝压测脚本
scp -P 9000 stress.sh root@100.64.249.217:/root

for i in 22 23 24 25 26 27 28 29 30 31 32
do
    scp stress.sh root@192.168.1.${i}:/root
done

# 取回压测脚本
for i in 22 23 24 25 26 27 28 29 30 31 32
do
    scp root@192.168.1.${i}:/root/node${i}_stress.log ./
done

# 拷贝clearwater配置
scp -P 9000 -r clearwater root@100.64.249.217:/root

# 安装zabbix-agent
for i in 22 23 24 25 26 27 28 29 30 31 32
do
    ssh root@192.168.1.${i} 'apt-get install zabbix-agent -y'
done

# 替换zabbix-agent配置文件
for i in 22 23 24 25 26 27 28 29 30 31 32
do
    ssh root@192.168.1.${i} sed -i "s/Server=127.0.0.1/Server=192.168.1.20/g" /etc/zabbix/zabbix_agentd.conf
    ssh root@192.168.1.${i} sed -i "s/ServerActive=127.0.0.1/ServerActive=192.168.1.20/g" /etc/zabbix/zabbix_agentd.conf
done

ssh root@192.168.1.23 'sed -i "s/Hostname=Zabbix server/Hostname=ubuntu23/g" /etc/zabbix/zabbix_agentd.conf' && \
ssh root@192.168.1.24 'sed -i "s/Hostname=Zabbix server/Hostname=ubuntu24/g" /etc/zabbix/zabbix_agentd.conf' && \
ssh root@192.168.1.25 'sed -i "s/Hostname=Zabbix server/Hostname=ubuntu25/g" /etc/zabbix/zabbix_agentd.conf' && \
ssh root@192.168.1.26 'sed -i "s/Hostname=Zabbix server/Hostname=ubuntu26/g" /etc/zabbix/zabbix_agentd.conf' && \
ssh root@192.168.1.27 'sed -i "s/Hostname=Zabbix server/Hostname=ubuntu27/g" /etc/zabbix/zabbix_agentd.conf' && \
ssh root@192.168.1.28 'sed -i "s/Hostname=Zabbix server/Hostname=ubuntu28/g" /etc/zabbix/zabbix_agentd.conf' && \
ssh root@192.168.1.29 'sed -i "s/Hostname=Zabbix server/Hostname=ubuntu29/g" /etc/zabbix/zabbix_agentd.conf' && \
ssh root@192.168.1.30 'sed -i "s/Hostname=Zabbix server/Hostname=ubuntu30/g" /etc/zabbix/zabbix_agentd.conf' && \
ssh root@192.168.1.31 'sed -i "s/Hostname=Zabbix server/Hostname=ubuntu31/g" /etc/zabbix/zabbix_agentd.conf' && \
ssh root@192.168.1.32 'sed -i "s/Hostname=Zabbix server/Hostname=ubuntu32/g" /etc/zabbix/zabbix_agentd.conf'

# 启动zabbix-agent服务
for i in 22 23 24 25 26 27 28 29 30 31 32
do
    ssh root@192.168.1.${i} service zabbix-agent restart
done

# docker pull image
for i in 22 23 24 25 26 27 28 29 30 31 32
do
    ssh root@192.168.1.${i} 
docker pull rainlf/clearwater-sprout && \
docker pull rainlf/clearwater-ralf && \
docker pull rainlf/clearwater-homestead-prov && \
docker pull rainlf/clearwater-homestead && \
docker pull rainlf/clearwater-homer && \
docker pull rainlf/clearwater-ellis && \
docker pull rainlf/clearwater-bono && \
docker pull rainlf/clearwater-chronos && \
docker pull rainlf/clearwater-cassandra && \
docker pull rainlf/clearwater-astaire && \
docker pull rainlf/clearwater-base
done



scp -r -P 9000 k8s_config/clearwater root@100.64.249.217:/root/cw

scp -P 9000 root@100.64.249.217:/tmp/10274.csv /tmp

# 压测
# 进入node24
docker exec -it $(docker ps |grep clearwater-cassandra |awk {'print $1'}) bash
    
/usr/share/clearwater/crest-prov/src/metaswitch/crest/tools/stress_provision.sh 500

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


# 配置静态IP
echo 'source /etc/network/interfaces.d/*
auto lo
iface lo inet loopback

auto ens160
iface ens160 inet static
address 192.168.1.13
gateway 192.168.1.1
netmask 255.255.255.0' > /etc/network/interfaces 

# 配置默认DNS
echo 'nameserver 192.168.1.1' > /etc/resolvconf/resolv.conf.d/base