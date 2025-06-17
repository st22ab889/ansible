



![](images/35FB28FF88BF4CBA9A6552D2A4E67239clipboard.png)





![](images/CA7AAD3D3F8E4E58AF5015259FD66432clipboard.png)

![](images/8A8C0EEA445B408A9873EBFAE397D0ACclipboard.png)





![](images/0AE43C818D494A829DD5D1665A8DE2ACclipboard.png)

```javascript
# cat config.j2
{#user variable example#}
welcome host {{ansible_hostname}}, os is {{ansible_os_family}}
today is {{ansible_date_time.date}}
cpu core numbers {{ansible_processor_vcpus}}

{#use condition example#}
{%if ansible_processor_vcpus >1%}
OS CPU more than one core
{%endif%}

{%for m in ansible_mounts if m['mount'] != "/"%}
mount {{m['mount']}}, total size is {{m['size_total']}}, free size is {{m['size_available']}}
{%endfor%}
```



```javascript
# cat example-task-playbook-jinja2.yaml
---
- name: a template example
  hosts: master
  remote_user: root
  tasks:
    - name: update jinja2 config
      template: src=config.j2 dest=/tmp/config.conf
```



```javascript
[root@localhost ~]# ansible-playbook -i hosts example-task-playbook-jinja2.yaml

PLAY [a template example] *******************************************************************......

TASK [Gathering Facts] **********************************************************************......
ok: [192.168.32.100]

TASK [update jinja2 config] *****************************************************************......
changed: [192.168.32.100]

PLAY RECAP **********************************************************************************......
192.168.32.100             : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

[root@localhost ~]# 

```





在 master 机器上验证：

![](images/6923DB6B29CC4E67BD146AEEA53C0C2Bclipboard.png)

