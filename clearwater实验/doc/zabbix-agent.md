#  监控主机配置
## 安装zabbix-agent

在每一台主机上安装zabbix-agent工具
```
for i in 22 23 24 25 26 27 28 29 30 31 32
do
    ssh root@192.168.1.${i} 'apt-get install zabbix-agent -y'
done
```

## 替换zabbix-agent配置文件
修改每一台主机的zabbix-agent配置文件，指明zabbix-server地址，指明Hostname(与页面配置保持一致)
```
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
```


## 启动zabbix-agent服务
```
for i in 22 23 24 25 26 27 28 29 30 31 32
do
    ssh root@192.168.1.${i} service zabbix-agent restart
done
```

## 页面配置
见：http://lab205.jios.org:12000/hosts.php?ddreset=1

Admin/zabbix