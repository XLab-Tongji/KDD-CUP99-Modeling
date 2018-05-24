# 205环境
1. 创建环境变量
kubectl create configmap env-vars --from-literal=ZONE=default.svc.cluster.local

2. 设置node label
kubectl label node node22 compoentType=astaire
kubectl label node node23 compoentType=bono
kubectl label node node24 compoentType=cassandra
kubectl label node node25 compoentType=chronos
kubectl label node node26 compoentType=ellis
kubectl label node node27 compoentType=etcd
kubectl label node node28 compoentType=homer
kubectl label node node29 compoentType=homestead
kubectl label node node30 compoentType=homestead-prov
kubectl label node node31 compoentType=ralf
kubectl label node node32 compoentType=sprout
kubectl label node node33 compoentType=stress_ng

3. 查看node label
kubectl get node --show-labels

4. 运行clearwater
kubectl apply -f clearwater-205

# 409环境
1. 创建环境变量
kubectl create configmap env-vars --from-literal=ZONE=default.svc.cluster.local

2. 运行clearwater
kubectl apply -f clearwater-409