1. SSH长连接

 SSH 长连接 需要  openssh版本 >= 5.6

```javascript
[root@localhost ~]# ssh -V
OpenSSH_7.4p1, OpenSSL 1.0.2k-fips  26 Jan 2017
```



```javascript
// 如果没有安装 SSH,使用下面的命令安装
// yum provides 查询 ssh 属于哪个软件包
yum provides ssh
yum install openssh-clients
// 如果要升级 ssh, 使用下面的命令
yum update ssh
```





改 ansible 配置文件 ：

```javascript
cat /etc/ansible/ansible.cfg
//......
#ssh_args = -C -o ControlMaster=auto -o ControlPersist=60s
//......

ControlPersist表示连接时间,默认为60s,表示长连接60s就断开,可以把这个值改大写。
去掉 ssh_args 前的注释,改为如下(86400s表示一天)：
ssh_args = -C -o ControlMaster=auto -o ControlPersist=86400s

```



```javascript
// 建立连接前先查看长连接信息
[root@localhost ~]# ss -nat
State       Recv-Q Send-Q                                                              Local Address:Port                                                                             Peer Address:Port              
LISTEN      0      128                                                                             *:22                                                                                          *:*                  
LISTEN      0      100                                                                     127.0.0.1:25                                                                                          *:*                  
ESTAB       0      36                                                                  192.168.32.99:22                                                                               192.168.32.1:59079              
LISTEN      0      128                                                                          [::]:22                                                                                       [::]:*                  
LISTEN      0      100                                                                         [::1]:25                                                                                       [::]:* 


// 修改完配置文件后,首先给机器建立第一次连接
[root@localhost ~]# ansible-playbook -i hosts checkhosts-one.yml --limit master
//......

// 建立连接后查看长连接信息, 可以看到多了一个 ESTAB, 超过 86400s 这个连接才断开
[root@localhost ~]# ss -nat
State       Recv-Q Send-Q                                                              Local Address:Port                                                                             Peer Address:Port              
LISTEN      0      128                                                                             *:22                                                                                          *:*                  
LISTEN      0      100                                                                     127.0.0.1:25                                                                                          *:*                  
ESTAB       0      0                                                                   192.168.32.99:39088                                                                          192.168.32.100:22                 
ESTAB       0      36                                                                  192.168.32.99:22                                                                               192.168.32.1:59079              
LISTEN      0      128                                                                          [::]:22                                                                                       [::]:*                  
LISTEN      0      100                                                                         [::1]:25                                                                                       [::]:*   
```





2. SS相关命令

```javascript
yum install iproute // iproute是linux平台强大的网络管理工具
ss -ntl  // 检查端口
ss -nat  // 查看连接
ss -nal
ss -atl
ss -ntal
```

