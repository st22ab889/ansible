1. 剧本变量定义在 Playbook 中, 它的定义方式有多种,这里介绍两种最常用的定义方式



1.1 通过 Playbook 的 vars 属性定义

```javascript
---
- name: test play vars
  hosts: all
  vars:
    user: lilei
    home: /home/lilei
```



当通过 vars 属性定义很多变量时, 这个 play 就会感觉特别臃肿, 此时可以将变量单独从 playbook 中抽离出来



1.2 通过 Playbook 的 vars_files 属性定义

```javascript
---
- name: test play vars
  hosts: all
  vars_files:
    - vars/users.yml
```



```javascript
# cat ./vars/users.yml
---
user: lilei
home: /home/lilei
```





2. 在 Playbook 中使用这些变量

```javascript
// 首先给本机建立连接
[root@localhost ~]# hostname -i
::1 127.0.0.1 192.168.32.99

[root@localhost ~]# ssh-copy-id root@192.168.32.99
/usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "/root/.ssh/id_rsa.pub"
The authenticity of host '192.168.32.99 (192.168.32.99)' can't be established.
ECDSA key fingerprint is SHA256:TcIIiLI+VCMoPspFCqRZHywv50EB/CMwDoIk6RxTB50.
ECDSA key fingerprint is MD5:43:cb:24:f0:02:26:58:6c:cf:1b:56:67:e5:50:be:30.
Are you sure you want to continue connecting (yes/no)? yes
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
/usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
root@192.168.32.99's password: // 输入 192.168.32.99 主机的密码

Number of key(s) added: 1

Now try logging into the machine, with:   "ssh 'root@192.168.32.99'"
and check to make sure that only the key(s) you wanted were added.

// 在上面的过程中要输入密码,如果没有密码要设置密码,"passwd"命令设置密码
[root@localhost ~]# passwd
Changing password for user root.
New password:
```



使用方式1（把变量定义在 Playbook 中）:

```javascript
# test_play_vars.yml
---
- name: test play vars
  hosts: all
  vars:
    user: lilei
    home: /home/lilei
  tasks:
    - name: create the user {{user}}
      user:
        # 下面使用变量一定要加上双引号
        name: "{{user}}"
        home: "{{home}}"
```



```javascript
[root@localhost ~]# ansible-playbook -i localhost, test_play_vars.yml -C

PLAY [test play vars] ******************************......

TASK [Gathering Facts] *****************************......
ok: [localhost]

TASK [create the user lilei] ***********************......
changed: [localhost]

PLAY RECAP *****************************************......
localhost                  : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0 
```





使用方式2（把变量定义在单独一个文件中）:

```javascript
# test2_play_vars.yml
---
- name: test play vars
  hosts: all
  vars_files:
    - users.yml
  tasks:
    - name: create the user {{user}}
      user:
        # 下面使用变量一定要加上双引号
        name: "{{user}}"
        home: "{{home}}"
```



```javascript
# users.yml
---
user: lilei
home: /home/lilei
```



```javascript
[root@localhost ~]# ansible-playbook -i localhost, test2_play_vars.yml -C

PLAY [test play vars] ********************************************......

TASK [Gathering Facts] *******************************************......
ok: [localhost]

TASK [create the user lilei] *************************************......
changed: [localhost]

PLAY RECAP *********************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

```

