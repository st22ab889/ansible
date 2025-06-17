1. debug

使用 "-v"参数对 ansible 的执行过程进行调试，有利于执行过程中的排错！



"-v" 中 v 的个数最多为5个，v 越多调试出来的信息越多，但是一般只用到 3 个 v，也就说是 -vvv

```javascript
# cat hosts
[master]
192.168.32.100
[node]
192.168.32.101
```



```javascript
[root@localhost ~]# ansible master -i hosts -m ping
192.168.32.100 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": false, 
    "ping": "pong"
}

// -v
[root@localhost ~]# ansible master -i hosts -m ping -v
Using /etc/ansible/ansible.cfg as config file
192.168.32.100 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": false, 
    "ping": "pong"
}

// -vv
[root@localhost ~]# ansible master -i hosts -m ping -vv
ansible 2.9.27
  config file = /etc/ansible/ansible.cfg
  configured module search path = [u'/root/.ansible/plugins/modules', u'/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python2.7/site-packages/ansible
  executable location = /usr/bin/ansible
  python version = 2.7.5 (default, Oct 14 2020, 14:45:30) [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
Using /etc/ansible/ansible.cfg as config file
Skipping callback 'actionable', as we already have a stdout callback.
Skipping callback 'counter_enabled', as we already have a stdout callback.
Skipping callback 'debug', as we already have a stdout callback.
Skipping callback 'dense', as we already have a stdout callback.
Skipping callback 'dense', as we already have a stdout callback.
Skipping callback 'full_skip', as we already have a stdout callback.
Skipping callback 'json', as we already have a stdout callback.
Skipping callback 'minimal', as we already have a stdout callback.
Skipping callback 'null', as we already have a stdout callback.
Skipping callback 'oneline', as we already have a stdout callback.
Skipping callback 'selective', as we already have a stdout callback.
Skipping callback 'skippy', as we already have a stdout callback.
Skipping callback 'stderr', as we already have a stdout callback.
Skipping callback 'unixy', as we already have a stdout callback.
Skipping callback 'yaml', as we already have a stdout callback.
META: ran handlers
192.168.32.100 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": false, 
    "ping": "pong"
}
META: ran handlers
META: ran handlers

// -vvv
[root@localhost ~]# ansible master -i hosts -m ping -vvv
ansible 2.9.27
  config file = /etc/ansible/ansible.cfg
  configured module search path = [u'/root/.ansible/plugins/modules', u'/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python2.7/site-packages/ansible
  executable location = /usr/bin/ansible
// 省略......

[root@localhost ~]# ansible master -i hosts -m ping -vvvv
// 省略......

[root@localhost ~]# ansible master -i hosts -m ping -vvvvv
// 省略......
```



2. --limit 参数可以用来选择资产中的组

```javascript
# cat checkhosts-one.yml
- hosts: all
  tasks:
    - name: check hosts
      ping:
      
```



```javascript
//虽然 play-book 中的 hosts 属性是all,但是仍然可以在命令行中使用 --limit 来选择组
[root@localhost ~]# ansible-playbook -i hosts checkhosts-one.yml --limit master

PLAY [all] ***************************************************......

TASK [Gathering Facts] ***************************************......
ok: [192.168.32.100]

TASK [check hosts] *******************************************......
ok: [192.168.32.100]

PLAY RECAP ***************************************************......
192.168.32.100             : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0  

//同样可以在 ansible-playbook 命令行中使用 "-v" 的方式来调试
[root@localhost ~]# ansible-playbook -i hosts checkhosts-one.yml --limit master -vv
ansible-playbook 2.9.27
  config file = /etc/ansible/ansible.cfg
  configured module search path = [u'/root/.ansible/plugins/modules', u'/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python2.7/site-packages/ansible
  executable location = /usr/bin/ansible-playbook
  python version = 2.7.5 (default, Oct 14 2020, 14:45:30) [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
Using /etc/ansible/ansible.cfg as config file
Skipping callback 'actionable', as we already have a stdout callback.
// 省略......
```

