实例演练



在 Ansible 中使用 Jinjia2 模板：

```javascript
# nginx.conf.j2
#user  nobody;

{#start process equal cpu cores#}
worker_processes  {{ansible_processor_vcpus}};

#error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

#pid        logs/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;

    #log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
    #                  '$status $body_bytes_sent "$http_referer" '
    #                  '"$http_user_agent" "$http_x_forwarded_for"';

    #access_log  logs/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    #keepalive_timeout  0;
    keepalive_timeout  65;

    #gzip  on;

    {#add_header {{ansible_hostname}};#}
    add_header x-hostname {{ansible_hostname}};

    server {
        listen       80;
        server_name  localhost;

        #charset koi8-r;

        #access_log  logs/host.access.log  main;

        location / {
            root   html;
            index  index.html index.htm;
        }

        #error_page  404              /404.html;

        # redirect server error pages to the static page /50x.html
        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }

        # proxy the PHP scripts to Apache listening on 127.0.0.1:80
        #
        #location ~ \.php$ {
        #    proxy_pass   http://127.0.0.1;
        #}

        # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
        #
        #location ~ \.php$ {
        #    root           html;
        #    fastcgi_pass   127.0.0.1:9000;
        #    fastcgi_index  index.php;
        #    fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;
        #    include        fastcgi_params;
        #}

        # deny access to .htaccess files, if Apache's document root
        # concurs with nginx's one
        #
        #location ~ /\.ht {
        #    deny  all;
        #}
    }


    # another virtual host using mix of IP-, name-, and port-based configuration
    #
    #server {
    #    listen       8000;
    #    listen       somename:8080;
    #    server_name  somename  alias  another.alias;

    #    location / {
    #        root   html;
    #        index  index.html index.htm;
    #    }
    #}


    # HTTPS server
    #
    #server {
    #    listen       443 ssl;
    #    server_name  localhost;

    #    ssl_certificate      cert.pem;
    #    ssl_certificate_key  cert.key;

    #    ssl_session_cache    shared:SSL:1m;
    #    ssl_session_timeout  5m;

    #    ssl_ciphers  HIGH:!aNULL:!MD5;
    #    ssl_prefer_server_ciphers  on;

    #    location / {
    #        root   html;
    #        index  index.html index.htm;
    #    }
    #}

}
```





继续优化PlayBook,让它支持模板：

```javascript
# cat example-task-playbook-jinja2-template.yaml
---
- name: template playbook example
  hosts: master
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
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      tags: tag_update_config
      notify: reload nginx server

    # 如果目标主机上的 www.example.com.conf 文件发生改变,就会运行 handlers 中的 reload nginx server 任务
    - name: add virtualhost config
      copy: 
        src: www.example.com.conf 
        dest: /etc/nginx/conf.d/
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

    - name: print nginx syntax
      debug: var=nginx_syntax_result

    - name: print nginx running
      debug: var=nginx_running_result

    - name: start nginx server
      systemd: name=nginx state=started
      when:
        - nginx_syntax_result.rc == 0  
        - nginx_running_result.stat.exists == false

  # handlers 里面也可以看作时包含了一些列的 task 任务
  handlers:
    - name: reload nginx server
      systemd: name=nginx state=reloaded
      # when 也可以用下面的方式表示 and 关系
      when:
        - nginx_syntax_result.rc == 0
        - nginx_running_result.stat.exists == true
```





运行 ansible-playbook 命令：

```javascript
[root@localhost ~]# ansible-playbook -i hosts example-task-playbook-jinja2-template.yaml

PLAY [template playbook example] *****************************************************************************************************************************************************************************

TASK [Gathering Facts] ***************************************************************************************************************************************************************************************
ok: [192.168.32.100]

TASK [create user] *******************************************************************************************************************************************************************************************
changed: [192.168.32.100] => (item=tomcat)
changed: [192.168.32.100] => (item=www)
changed: [192.168.32.100] => (item=mysql)

TASK [yum nginx master] **************************************************************************************************************************************************************************************
ok: [192.168.32.100]

TASK [update nginx main config] ******************************************************************************************************************************************************************************
changed: [192.168.32.100]

TASK [add virtualhost config] ********************************************************************************************************************************************************************************
ok: [192.168.32.100]

TASK [check nginx syntax] ************************************************************************************************************************************************************************************
changed: [192.168.32.100]

TASK [check nginx running] ***********************************************************************************************************************************************************************************
ok: [192.168.32.100]

TASK [print nginx syntax] ************************************************************************************************************************************************************************************
ok: [192.168.32.100] => {
    "nginx_syntax_result": {
        "changed": true, 
        "cmd": "/usr/sbin/nginx -t", 
        "delta": "0:00:00.009777", 
        "end": "2022-05-04 02:31:42.011562", 
        "failed": false, 
        "rc": 0, 
        "start": "2022-05-04 02:31:42.001785", 
        "stderr": "nginx: the configuration file /etc/nginx/nginx.conf syntax is ok\nnginx: configuration file /etc/nginx/nginx.conf test is successful", 
        "stderr_lines": [
            "nginx: the configuration file /etc/nginx/nginx.conf syntax is ok", 
            "nginx: configuration file /etc/nginx/nginx.conf test is successful"
        ], 
        "stdout": "", 
        "stdout_lines": []
    }
}

TASK [print nginx running] ***********************************************************************************************************************************************************************************
ok: [192.168.32.100] => {
    "nginx_running_result": {
        "changed": false, 
        "failed": false, 
        "stat": {
            "atime": 1651642913.0076973, 
            "attr_flags": "", 
            "attributes": [], 
            "block_size": 4096, 
            "blocks": 8, 
            "charset": "us-ascii", 
            "checksum": "fd132cf018790c13a6f9c4e9f805966d684509c9", 
            "ctime": 1651642913.0076973, 
            "dev": 20, 
            "device_type": 0, 
            "executable": false, 
            "exists": true, 
            "gid": 0, 
            "gr_name": "root", 
            "inode": 30788, 
            "isblk": false, 
            "ischr": false, 
            "isdir": false, 
            "isfifo": false, 
            "isgid": false, 
            "islnk": false, 
            "isreg": true, 
            "issock": false, 
            "isuid": false, 
            "mimetype": "text/plain", 
            "mode": "0644", 
            "mtime": 1651642913.0076973, 
            "nlink": 1, 
            "path": "/var/run/nginx.pid", 
            "pw_name": "root", 
            "readable": true, 
            "rgrp": true, 
            "roth": true, 
            "rusr": true, 
            "size": 5, 
            "uid": 0, 
            "version": null, 
            "wgrp": false, 
            "woth": false, 
            "writeable": true, 
            "wusr": true, 
            "xgrp": false, 
            "xoth": false, 
            "xusr": false
        }
    }
}

TASK [start nginx server] ************************************************************************************************************************************************************************************
skipping: [192.168.32.100]

RUNNING HANDLER [reload nginx server] ************************************************************************************************************************************************************************
changed: [192.168.32.100]

PLAY RECAP ***************************************************************************************************************************************************************************************************
192.168.32.100             : ok=10   changed=4    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   

[root@localhost ~]#
```





在 master 机器上验证：

```javascript
[root@centos7 aaron]# hostname
centos7.master
[root@centos7 aaron]# 
[root@centos7 aaron]# hostname -i
127.0.0.1 192.168.32.100
[root@centos7 aaron]# 
[root@centos7 aaron]# cat /etc/nginx/nginx.conf 

#user  nobody;

worker_processes  2;

#error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

#pid        logs/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;

    #log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
    #                  '$status $body_bytes_sent "$http_referer" '
    #                  '"$http_user_agent" "$http_x_forwarded_for"';

    #access_log  logs/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    #keepalive_timeout  0;
    keepalive_timeout  65;

    #gzip  on;

        add_header x-hostname centos7;

    server {
        listen       80;
        server_name  localhost;
// 省略......
[root@centos7 aaron]#
```

