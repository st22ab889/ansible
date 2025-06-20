1. Facts 变量介绍

![](images/5059B656C844460BAA16288FCD6DEF83clipboard.png)





2. 手动收集 Facts 变量

```javascript

// ansible all -i localhost, -m setup  # 这个命令可以看到全部的键

// "-c"参数表示连接类型
[root@localhost ~]# ansible all -i localhost, -c local -m setup
localhost | SUCCESS => {
    "ansible_facts": {
        "ansible_all_ipv4_addresses": [
            "192.168.32.99"
        ], 
        "ansible_all_ipv6_addresses": [
            "fe80::63f0:573c:d981:1961"
        ], 
        "ansible_apparmor": {
            "status": "disabled"
        }, 
        "ansible_architecture": "x86_64", 
        "ansible_bios_date": "07/22/2020", 
        "ansible_bios_version": "6.00",
        // ......		
        "ansible_system_capabilities_enforced": "True", 
        "ansible_system_vendor": "VMware, Inc.", 
        "ansible_uptime_seconds": 5777, 
        "ansible_user_dir": "/root", 
        "ansible_user_gecos": "root", 
        "ansible_user_gid": 0, 
        "ansible_user_id": "root", 
        "ansible_user_shell": "/bin/bash", 
        "ansible_user_uid": 0, 
        "ansible_userspace_architecture": "x86_64", 
        "ansible_userspace_bits": "64", 
        "ansible_virtualization_role": "guest", 
        "ansible_virtualization_type": "VMware", 
        "discovered_interpreter_python": "/usr/bin/python", 
        "gather_subset": [
            "all"
        ], 
        "module_setup": true
    }, 
    "changed": false
}
[root@localhost ~]# 
```

注意：如果是容器可能有些信息获取不到。





3. 过滤 Facts

上面收集的 Facts 信息量很大, 可以通过使用 Facts 模块中的 filter 参数过滤出需要的信息。

```javascript
// 仅获取服务器的内存情况信息
// "-c"参数表示连接类型, "-c local"表示不走 ssh 通道, 不走 ssh 通道会快些
[root@localhost ~]# ansible all -i localhost, -c local -m setup -a "filter=*memory*"
localhost | SUCCESS => {
    "ansible_facts": {
        "ansible_memory_mb": {
            "nocache": {
                "free": 3374, 
                "used": 396
            }, 
            "real": {
                "free": 3243, 
                "total": 3770, 
                "used": 527
            }, 
            "swap": {
                "cached": 0, 
                "free": 3967, 
                "total": 3967, 
                "used": 0
            }
        }, 
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": false
}

// 仅获取服务器的磁盘挂载情况
[root@localhost ~]# ansible all -i localhost, -c local -m setup -a "filter=*mount*"
localhost | SUCCESS => {
    "ansible_facts": {
        "ansible_mounts": [
            {
                "block_available": 221157, 
                "block_size": 4096, 
                "block_total": 259584, 
                "block_used": 38427, 
                "device": "/dev/sda1", 
                "fstype": "xfs", 
                "inode_available": 523961, 
                "inode_total": 524288, 
                "inode_used": 327, 
                "mount": "/boot", 
                "options": "rw,seclabel,relatime,attr2,inode64,noquota", 
                "size_available": 905859072, 
                "size_total": 1063256064, 
                "uuid": "5749bb60-3729-4dfb-84dd-232108cc4944"
            }, 
            {
                "block_available": 8658701, 
                "block_size": 4096, 
                "block_total": 9201265, 
                "block_used": 542564, 
                "device": "/dev/mapper/centos-root", 
                "fstype": "xfs", 
                "inode_available": 18356271, 
                "inode_total": 18411520, 
                "inode_used": 55249, 
                "mount": "/", 
                "options": "rw,seclabel,relatime,attr2,inode64,noquota", 
                "size_available": 35466039296, 
                "size_total": 37688381440, 
                "uuid": "6048e3e7-c9d9-4ebc-b0fa-ba0aa27ddfa6"
            }
        ], 
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": false
}
```

注意：过滤的东西必须在 ansible 的 setup 模块中有那个键，没有这个健过滤不了！





4. 在 Playbook 中使用 Facts 变量

```javascript
# cat hosts
[master]
192.168.32.100
[node]
192.168.32.101
```



```javascript
#  cat example-task-playbook-facts.yaml
---
- name: the first play example
  hosts: master
  remote_user: root
  tasks:
    - name: install nginx package
      yum: name=nginx state=present
    - name: copy nginx.conf to remote server
      copy: src=nginx.conf dest=/etc/nginx/nginx.conf
    - name: start nginx server
      systemd:
        name: nginx
        enabled: true
        state: started
---        
- name: print facts variable
  hosts: master
  tasks: 
    - name: print facts variable
      debug:
        # 使用 Facts 变量
        msg: "the default IPV4 address is {{ansible_default_ipv4.address}}"
```

注意：拿key的时候要注意层级，如果要拿里面的要先拿到最外边，这是嵌套的，最外面的key一般都是ansible开头的。例如：

```javascript
{{ansible_default_ipv4.address}}
```





```javascript
[root@localhost ~]# ansible-playbook -i hosts example-task-playbook-facts.yaml 

PLAY [the first play example] *********************************************......

# 执行 Playbook 时, 自动收集 facts 信息
TASK [Gathering Facts] ****************************************************......
ok: [192.168.32.100]

TASK [install nginx package] **********************************************......
ok: [192.168.32.100]

TASK [copy nginx.conf to remote server] ***********************************......
ok: [192.168.32.100]

TASK [start nginx server] *************************************************......
ok: [192.168.32.100]

PLAY [print facts variable] ***********************************************......

TASK [Gathering Facts] ****************************************************......
ok: [192.168.32.100]

# 这里就能拿到 facts 变量值
TASK [print facts variable] ***********************************************......
ok: [192.168.32.100] => {
    "msg": "the default IPV4 address is 192.168.32.100"
}

PLAY RECAP ******************************************************************
192.168.32.100             : ok=6    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0  
```



