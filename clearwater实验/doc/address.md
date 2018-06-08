# Address

Environment address:
- Rancher http://lab205.jios.org:9002/env/1a7/kubernetes/dashboard
- Kubernets http://lab205.jios.org:9002/r/projects/1a7/kubernetes-dashboard:9090/#!/overview?namespace=default
- Grafana http://lab205.jios.org:30002/dashboard/db/cluster?orgId=1
---
How to ssh to environment?
```
ssh -p 9000 root@lab205.jios.org
```
---
Can't accsee grafana web page?
- enter the kubernetes web page
- choice **kube-system** namespace
- edit *monitoring-grafana* service in serivce list as:
```
"spec": {
    "ports": [
      {
        "protocol": "TCP",
        "port": 80,
        "targetPort": 3000, # change here
        "nodePort": 30002
      }
    ],
    "type": "NodePort", # and here
    ...
  },
```
---
Port forwarding

- zabbix-server

dest address | port | src address | port
:-: | :-: | :-: | :-:
lab205.jios.org | 5678 | 192.168.1.20 | 5678
lab205.jios.org | 9000 | 192.168.1.20 | 22
lab205.jios.org | 9003 | 192.168.1.20 | 8388
lab205.jios.org | 9004 | 192.168.1.20 | 3000
lab205.jios.org | 9006 | 192.168.1.20 | 8081
lab205.jios.org | 12000 | 192.168.1.20 | 80
lab205.jios.org | 12001 | 192.168.1.20 | 3306
lab205.jios.org | 12002 | 192.168.1.20 | 8080

- jenkins-host

dest address | port | src address | port
:-: | :-: | :-: | :-:
lab205.jios.org | 3333 | 192.168.1.20 | 22
lab205.jios.org | 3334 | 192.168.1.20 | 8080
lab205.jios.org | 3335 | 192.168.1.20 | 8112
lab205.jios.org | 3336 | 192.168.1.20 | 8113
lab205.jios.org | 3337 | 192.168.1.20 | 27017
lab205.jios.org | 11001 | 192.168.1.20 | 80
lab205.jios.org | 11081 | 192.168.1.20 | 8080

- others

dest address | port | src address | port
:-: | :-: | :-: | :-:
lab205.jios.org | 11002 | 192.168.1.12 | 80
lab205.jios.org | 11082 | 192.168.1.12 | 8080
lab205.jios.org | 11003 | 192.168.1.20 | 80
lab205.jios.org | 11083 | 192.168.1.20 | 8080
lab205.jios.org | 9005 | 192.168.1.21 | 443
lab205.jios.org | 30001 | 192.168.1.22 | 30001
lab205.jios.org | 30002 | 192.168.1.22 | 30002