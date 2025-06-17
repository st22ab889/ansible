1. copy 模块

copy 模块主要用于管理节点和被管理节点之间的文件拷贝。

```javascript
// 在管理节点上创建 test.txt 文件
[root@localhost ~]# echo  "touch this is test file" > test.txt
[root@localhost ~]# cat test.txt 
touch this is test file
[root@localhost ~]# ls /root/test.txt 
/root/test.txt

// copy 管理节点上的 test.txt 到被管理节点上
// 注意：被管理节点的目录要存在，否则会拷贝失败
[root@localhost ~]# ansible master -i hosts -m copy -a "src=./test.txt dest=/tmp/test.txt"
192.168.32.100 | CHANGED => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": true, 
    "checksum": "ed51941db72448f9fcaf336f4509f229499c96d9", 
    "dest": "/tmp/test.txt", 
    "gid": 0, 
    "group": "root", 
    "md5sum": "7cc68987bfd94d874513177151d14fec", 
    "mode": "0644", 
    "owner": "root", 
    "secontext": "unconfined_u:object_r:admin_home_t:s0", 
    "size": 24, 
    "src": "/root/.ansible/tmp/ansible-tmp-1650303807.51-2852-169610206177763/source", 
    "state": "file", 
    "uid": 0
}


```



 copy 前，在被管理节点上对原文件进行备份:

```javascript
// 再次拷贝前,首先要更改一下文件,因为ansible是幂等的,会对文件进行md5校验。
// 如果文件没有更改,并不会进行实际的文件拷贝
[root@localhost ~]# echo  "touch this is test file2" > test.txt
[root@localhost ~]# cat test.txt 
touch this is test file2
[root@localhost ~]# ls /root/test.txt 
/root/test.txt

// 使用参数 backup=yes
[root@localhost ~]# ansible master -i hosts -m copy -a "src=./test.txt dest=/tmp/test.txt backup=yes"
192.168.32.100 | CHANGED => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "backup_file": "/tmp/test.txt.23184.2022-04-18@13:50:10~", 
    "changed": true, 
    "checksum": "c329f6c984c0d757e8764f72ac29727b43440cc8", 
    "dest": "/tmp/test.txt", 
    "gid": 0, 
    "group": "root", 
    "md5sum": "0df1b521d96ab52c598bff459ae14528", 
    "mode": "0644", 
    "owner": "root", 
    "secontext": "unconfined_u:object_r:admin_home_t:s0", 
    "size": 25, 
    "src": "/root/.ansible/tmp/ansible-tmp-1650304210.22-2935-270791239006728/source", 
    "state": "file", 
    "uid": 0
}

// 验证
[root@localhost ~]# ansible master -i hosts -m shell -a "ls -l /tmp"
192.168.32.100 | CHANGED | rc=0 >>
total 8
-rw-r--r--. 1 root root  0 Apr 14 12:47 a.conf
drwx------. 2 root root 41 Apr 18 13:50 ansible_command_payload_ZflscL
drwx------. 3 root root 17 Apr 18 11:03 systemd-private-b01674f1b56d43ada2528463f64bbf7c-chronyd.service-nSm2qV
-rw-r--r--. 1 root root  0 Apr 18 13:31 testfile
-rw-r--r--. 1 root root 25 Apr 18 13:50 test.txt
-rw-r--r--. 1 root root 24 Apr 18 13:43 test.txt.23184.2022-04-18@13:50:10~

// 总结：
// 拷贝文件时,只有文件改变才会备份,如果没有改变不会备份.
// 因为ansible执行命令都是等幂操作，就是说连续执行多条命令,如果能达到期望值就不会改变，就不会重复操作,因为会去校验文件的md5值
```





copy 文件的同时对文件进行用户及用户组设置:

```javascript
// aaron 这个用户名必须是要在目标机器上存在
[root@localhost ~]# ansible master -i hosts -m copy -a "src=./test.txt dest=/tmp/test.txt owner=aaron"
192.168.32.100 | CHANGED => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": true, 
    "checksum": "c329f6c984c0d757e8764f72ac29727b43440cc8", 
    "dest": "/tmp/test.txt", 
    "gid": 0, 
    "group": "root", 
    "mode": "0644", 
    "owner": "aaron", 
    "path": "/tmp/test.txt", 
    "secontext": "unconfined_u:object_r:admin_home_t:s0", 
    "size": 25, 
    "state": "file", 
    "uid": 1000
}

[root@localhost ~]# ansible master -i hosts -m shell -a "ls -l /tmp/test.txt"
192.168.32.100 | CHANGED | rc=0 >>
-rw-r--r--. 1 aaron root 25 Apr 18 13:50 /tmp/test.txt
```



copy 文件的同时对文件进行权限设置:

```javascript
[root@localhost ~]# ansible master -i hosts -m copy -a "src=./test.txt dest=/tmp/test.txt mode=0755"
192.168.32.100 | CHANGED => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": true, 
    "checksum": "c329f6c984c0d757e8764f72ac29727b43440cc8", 
    "dest": "/tmp/test.txt", 
    "gid": 0, 
    "group": "root", 
    "mode": "0755", 
    "owner": "aaron", 
    "path": "/tmp/test.txt", 
    "secontext": "unconfined_u:object_r:admin_home_t:s0", 
    "size": 25, 
    "state": "file", 
    "uid": 1000
}

[root@localhost ~]# ansible master -i hosts -m shell -a "ls -l /tmp/test.txt"
192.168.32.100 | CHANGED | rc=0 >>
-rwxr-xr-x. 1 aaron root 25 Apr 18 13:50 /tmp/test.txt

// 如果拷贝的文件目标主机没有,那就是这个文件默认是属于 root 用户和 root 这个组.
//  如果拷贝的文件目标主机存在,就仅仅改变权限.
```

