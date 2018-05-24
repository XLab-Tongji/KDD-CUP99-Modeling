# 数据收集过程
1. 进入跳板机
```
sshpass -p 123456 ssh -p 9000 root@100.64.249.217
```
2. 运行clearwater工作负载
```
# 跳板机中
## 查看clearwater pods情况
kubectl get pods

## 删除clearwater pods情况
kubectl delete -f cw

## 部署clearwater pods
kubectl apply -f cw

# 创建clearwater用户
## 进入node24
./connect.sh 24

## 进入clearwater-cassandra容器
docker exec -it $(docker ps |grep clearwater-cassandra |awk {'print $1'}) bash

## 生成用户（例：20000）
/usr/share/clearwater/crest-prov/src/metaswitch/crest/tools/stress_provision.sh 10000

# 压测
## 进入node32
./connect.sh 32

## 进入clearwater-sprout容器
docker exec -it $(docker ps |grep clearwater-sprout |awk {'print $1'} | head -1) bash

## 安装压测工具
apt-get update
apt-get install clearwater-sip-stress-coreonly -y

## 开始压测（例：20000用户，100分钟，clearwater-sprout容器ip:10.42.13.205）
/usr/share/clearwater/bin/run_stress default.svc.cluster.local \
            20000 100  --initial-reg-rate 100 \
            --icscf-target 10.42.13.205:5052 \
            --scscf-target 10.42.13.205:5054
```
3. 随机注入故障
```
# 注入时间100min
./stress.py 100
```
4. 收集数据
http://100.64.249.217:12002/swagger-ui.html
5. 清洗数据
