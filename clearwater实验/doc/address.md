# Address

Environment address:
- Rancher http://lab205.jios.org:9002/env/1a7/kubernetes/dashboard
- Kubernets http://lab205.jios.org:9002/r/projects/1a7/kubernetes-dashboard:9090/#!/overview?namespace=default
- Grafana http://lab205.jios.org:30002/dashboard/db/cluster?orgId=1
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
lab205.jios.org | 3333 | 192.168.1.11 | 22
lab205.jios.org | 3334 | 192.168.1.11 | 8080
lab205.jios.org | 3335 | 192.168.1.11 | 8112
lab205.jios.org | 3336 | 192.168.1.11 | 8113
lab205.jios.org | 3337 | 192.168.1.11 | 27017
lab205.jios.org | 3338 | 192.168.1.11 | 8114
lab205.jios.org | 11001 | 192.168.1.11 | 80
lab205.jios.org | 11081 | 192.168.1.11 | 8080

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
