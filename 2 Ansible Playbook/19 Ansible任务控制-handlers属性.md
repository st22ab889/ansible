1. handlers属性

使用 tags 后，Playbook 还是存在问题，当配置文件没有发生变化时，每次依然都会触发 TASK。只有配置文件发生变化的时候才触发 TASK，这样的处理才是最完美的实现，可以使用 handlers 属性实现这个功能。



改进后的 Playbook 如下：

```javascript
# cat example-task-playbook-handlers.yaml
---
- name: handlers playbook example
  hosts: master
  gather_facts: no
  vars:
    createUser:
      - tomcat
      - www
      - mysql
  tasks:
    - name: create user
      user: name={{item}} state=present
      with_items: "{{createUser}}"

    - name: yum nginx master
      yum: name=nginx state=present

    # 如果目标主机上的 nginx.conf 文件发生改变,就会运行 handlers 中的 reload nginx server 任务
    - name: update nginx main config
      copy: src=nginx.conf dest=/etc/nginx/
      tags: tag_update_config
      notify: reload nginx server

    # 如果目标主机上的 www.example.com.conf 文件发生改变,就会运行 handlers 中的 reload nginx server 任务
    - name: add virtualhost config
      copy: src=www.example.com.conf dest=/etc/nginx/conf.d/
      tags: tag_update_config
      notify: reload nginx server
    
    - name: check nginx syntax
      shell: /usr/sbin/nginx -t
      register: nginx_syntax_result
      tags: tag_update_config

    - name: check nginx running
      stat: path=/var/run/nginx.pid
      register: nginx_running_result
      tags: tag_update_config

    #- name: print nginx syntax
    #  debug: var=nginx_syntax_result

    #- name: print nginx running
    #  debug: var=nginx_running_result

    - name: start nginx server
      systemd: name=nginx state=started
      when: nginx_syntax_result.rc == 0 and nginx_running_result.stat.exists == false

  # handlers 里面也可以看作时包含了一些列的 task 任务
  handlers:
    - name: reload nginx server
      systemd: name=nginx state=reloaded
      # when 也可以用下面的方式表示 and 关系
      when:
        - nginx_syntax_result.rc == 0
        - nginx_running_result.stat.exists == true

```





```javascript
// 语法检查
[root@localhost ~]# ansible-playbook -i hosts example-task-playbook-handlers.yaml --syntax-check

playbook: example-task-playbook-handlers.yaml

// "-C"参数测试运行 Playbook (task不会在远程服务器上运行,所以运行都是默认行为)
[root@localhost ~]# ansible-playbook -i hosts example-task-playbook-handlers.yaml -t tag_update_config -C

// 首次运行,若配置文件没有发生变化,可以发现不会触发 handlers 中的 task 任务
[root@localhost ~]# ansible-playbook -i hosts example-task-playbook-handlers.yaml -t tag_update_config

PLAY [handlers playbook example] ************************************************************......

TASK [update nginx main config] *************************************************************......
ok: [192.168.32.100]

TASK [add virtualhost config] ***************************************************************......
ok: [192.168.32.100]

TASK [check nginx syntax] *******************************************************************......
changed: [192.168.32.100]

TASK [check nginx running] ******************************************************************......
ok: [192.168.32.100]

PLAY RECAP **********************************************************************************......
192.168.32.100             : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0


// 简单修改 nginx.conf 和 www.example.com.conf 这两个文件,只要 MD5 校验值发生变化即可。
// 比如增加或减少一个空格, MD5 校验值发生变化, ansible 就能识别到文件发生了变更。


// 再次运行,可以发现触发了 handles 中的 task 任务
[root@localhost ~]# ansible-playbook -i hosts example-task-playbook-handlers.yaml -t tag_update_config

PLAY [handlers playbook example] ************************************************************......

TASK [update nginx main config] *************************************************************......
changed: [192.168.32.100]

TASK [add virtualhost config] ***************************************************************......
changed: [192.168.32.100]

TASK [check nginx syntax] *******************************************************************......
changed: [192.168.32.100]

TASK [check nginx running] ******************************************************************......
ok: [192.168.32.100]

RUNNING HANDLER [reload nginx server] *******************************************************......
changed: [192.168.32.100]

PLAY RECAP **********************************************************************************......
192.168.32.100             : ok=5    changed=4    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```





2. 总结

在改进的 Playbook 中，"update nginx main config" 和"add virtualhost config" 这两个文件发布的 task 任务增加了新属性 notify，值为 "reload nginx server"。意思是对这两个文件发布的 task 设置一个通知机制，当 Ansible 认为文件的内容发生了变化(文件MD5发生变化)，它就会发送一个通知信号，通知 handlers 中的某一个任务。具体发送到 handlers 中的哪个任务，由 notify 的值决定，这个值会去匹配 handlers 中 task 的名称，如果匹配上就会运行这个 task，如果没有匹配上则什么也不做。注意：若要实现这样的机制，千万要注意 notify 属性设置的值，一定要确保能和 handlers 中的 task 名称对应上。







