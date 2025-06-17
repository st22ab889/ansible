1. 在 Playbook 中关闭 Facts 变量的获取

如果在整个 playbook 的执行过程中, 完全未使用过 Facts 变量, 此时可以将其关闭, 以加快playbook的执行速度。



```javascript
# cat hosts
[master]
192.168.32.100
[node]
192.168.32.101
```



```javascript
# cat example-task-playbook-nofacts .yaml

---
- name: the first play example
  hosts: master
  # 配置 gather_facts 的值为 no 就是关闭 facts 变量收集功能, 不配置或配置的值为 yes 就是获取 facts 变量
  gather_facts: no
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
        
```



```javascript
// 运行 Playbook
[root@localhost ~]# ansible-playbook -i hosts example-task-playbook-nofacts.yaml 

PLAY [the first play example] ************************************************......

# 可以看到这里已经少了收集 facts 信息的步骤

TASK [install nginx package] *************************************************......
ok: [192.168.32.100]

TASK [copy nginx.conf to remote server] **************************************......
ok: [192.168.32.100]

TASK [start nginx server] ****************************************************......
ok: [192.168.32.100]

PLAY RECAP *******************************************************************......
192.168.32.100             : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0 
 
```

