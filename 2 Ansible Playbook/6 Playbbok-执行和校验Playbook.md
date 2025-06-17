1. 准备工作 

Playbook 文件

```javascript
# example-task-playbook.yaml
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
```



准备  nginx.conf

```javascript
# nginx.conf

#user  nobody;
worker_processes  1;

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



2.使用 "--syntax-check" 对 Playbook 进行语法校验

```javascript
// 这种方法只能校验 Playbook 是否正确,不能校验 YAML 文件是否语法正确
// 如果没有使用 -i 指定资产,就使用的是默认资产,也可以把自己的资产配置为默认资产
[root@localhost ~]# ansible-playbook -i hosts example-task-playbook.yaml  --syntax-check

playbook: example-task-playbook.yaml

因为 Playbook 属于YAML格式,所以可以使用检查 YAML 语法格式的方法检查 Playbook 语法正确性

```



3.  使用 "-C" 参数测试运行 Playbook

使用 "-C" 参数会执行完整个 Playbook, 但是所有 Task 中的行为都不会在远程服务器上执行, 所有执行都是模拟行为。 

```javascript
[root@localhost ~]# ansible-playbook -i hosts example-task-playbook.yaml  -C

PLAY [the first play example] ******************************************......

TASK [Gathering Facts] *****************************************************......
ok: [192.168.32.100]

TASK [install nginx package] ***********************************************......
changed: [192.168.32.100]

TASK [copy nginx.conf to remote server] ************************************......
changed: [192.168.32.100]

TASK [start nginx server] *****************************************************......
changed: [192.168.32.100]

PLAY RECAP *************************************************************************......
192.168.32.100             : ok=4    changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0 
```





4. 使用 " --step" 单步跟从调试  Playbook 

```javascript
// (N)o/(y)es/(c)ontinue  
//    N 表示不运行这一步 task
//    y 表示单步运行到下一个task
//    c 表示退出调试模式,直接运行完接下来所有的 task
[root@localhost ~]# ansible-playbook -i hosts example-task-playbook.yaml  --step

PLAY [the first play example] ***************************************......
Perform task: TASK: Gathering Facts (N)o/(y)es/(c)ontinue: n

Perform task: TASK: Gathering Facts (N)o/(y)es/(c)ontinue: ***************......
Perform task: TASK: install nginx package (N)o/(y)es/(c)ontinue: y

Perform task: TASK: install nginx package (N)o/(y)es/(c)ontinue: **************......

TASK [install nginx package] **********************************************......
ok: [192.168.32.100]
Perform task: TASK: copy nginx.conf to remote server (N)o/(y)es/(c)ontinue: c

Perform task: TASK: copy nginx.conf to remote server (N)o/(y)es/(c)ontinue: **************......

TASK [copy nginx.conf to remote server] ***************************************......
ok: [192.168.32.100]

TASK [start nginx server] *******************************************************......
ok: [192.168.32.100]

PLAY RECAP ***************************************************************************......
192.168.32.100             : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0 

// 这个访问 nginx 成功, "404 Not Found"表示没有访问到 nginx 主页
[root@localhost ~]# ansible master -i hosts -m shell -a "curl 192.168.32.100"
[WARNING]: Consider using the get_url or uri module rather than running 'curl'.  //......
'command_warnings=False' in ansible.cfg to get rid of this message.
192.168.32.100 | CHANGED | rc=0 >>
<html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
<hr><center>nginx/1.20.2</center>
</body>
</html>  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
```





5. 直接运行  Playbook

```javascript
ansible-playbook -i hosts example-task-playbook.yaml
```

