1. 给远程的被管理节点添加yaml仓库源

```javascript
//命令中里面是单引号,外面就用双引号;里面是双引号,外面就用单引号
// 注意：这里的name参数是仓库文件中第一行的中括号中的名称
[root@localhost ~]# ansible master -i hosts -m yum_repository -a "name=epel baseurl='https://download.test.org/eael' description='EAEL YUM repo'"
192.168.32.100 | CHANGED => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": true, 
    "repo": "epel", 
    "state": "present"
}

// 下面[epel]中的epel就是仓库名称
[root@localhost ~]# ansible master -i hosts -m shell -a "cat /etc/yum.repos.d/epel.repo"
192.168.32.100 | CHANGED | rc=0 >>
[epel]
baseurl = https://download.test.org/eael
name = EAEL YUM repo

```



2. 删除源

```javascript
// 指定源名字,状态置为 absent 就可以删除源.
// 注意：要管理的这个东西必须是ansible 管理过的，没有管理过就执行不了
[root@localhost ~]# ansible master -i hosts -m yum_repository -a "name=epel state=absent"
192.168.32.100 | CHANGED => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": true, 
    "repo": "epel", 
    "state": "absent"
}

// 可以看到 epel.repo 已经被删除
[root@localhost ~]# ansible master -i hosts -m shell -a "ls /etc/yum.repos.d/"
192.168.32.100 | CHANGED | rc=0 >>
CentOS-Base.repo
CentOS-CR.repo
CentOS-Debuginfo.repo
CentOS-fasttrack.repo
CentOS-Media.repo
CentOS-Sources.repo
CentOS-Vault.repo
CentOS-x86_64-kernel.repo
docker-ce.repo
kubernetes.repo
```

