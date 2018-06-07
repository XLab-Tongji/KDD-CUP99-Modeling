# Address

Environment address:
- Rancher http://lab205.jios.org:9002/env/1a7/kubernetes/dashboard
- Kubernets http://lab205.jios.org:9002/r/projects/1a7/kubernetes-dashboard:9090/#!/overview?namespace=default
- Grafana http://lab205.jios.org:30002/dashboard/db/cluster?orgId=1

How to ssh to environment?
```
ssh -p 9000 root@lab205.jios.org
```

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