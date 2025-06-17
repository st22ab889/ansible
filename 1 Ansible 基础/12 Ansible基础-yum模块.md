1. 等同于 Linux 上的 YUM 命令,对远程服务器上 RPM 包进行管理：



YUM 模块参数：

- name 要安装的软件包名,多个软件包以英文逗号(,)隔开。

- state 对当前指定的软件安装、移除操作，支持的参数如下：

- present 确认已经安装，但不升级

- installed 确认已经安装

- latest 确保安装，且升级为最新

- absent 和 removed 确认已移除

```javascript
centos 安装 ngxin:
http://nginx.org/en/linux_packages.html
https://blog.csdn.net/Virgo626249038/article/details/121144722    
```



```javascript
// 首先要安装 nginx 的 yum 源. 
// 注意: 这里要使用 \ 符号去转义 $ 符号,否则 $ 及后面的字符串不能传输到主机
[root@localhost ~]# ansible master -i hosts -m yum_repository -a "name=nginx \
	baseurl='http://nginx.org/packages/centos/\$releasever/\$basearch/' \
	description='nginx stable repo' \
	gpgcheck=1 \
	enabled=1 \
	gpgkey='https://nginx.org/keys/nginx_signing.key' "
192.168.32.100 | CHANGED => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": true, 
    "repo": "nginx", 
    "state": "present"
}

// 安装软件包,install 和 present 效果差不多
[root@localhost ~]# ansible master -i hosts -m yum -a "name=nginx state=present"
192.168.32.100 | CHANGED => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": true, 
    "changes": {
        "installed": [
            "nginx"
        ]
    }, 
    "msg": "warning: ......", 
    "rc": 0, 
    "results": [
        "Loaded plugins: ......"
    ]
}

// 使用下面的命令也可以安装
//  ansible master -i hosts -m yum -a "name=nginx state=installed"
//  ansible master -i hosts -m yum -a "name=nginx state=latest"
```



```javascript
// 下面两个命令都可以移除软件包, absent 和 removed 效果一样，区别不大
 ansible master -i hosts -m yum -a "name=nginx state=absent"
 ansible master -i hosts -m yum -a "name=nginx state=removed"
 
// 删除YUM源
//   ansible master -i hosts -m yum_repository -a "name=nginx state=absent"
```



```javascript
// 安装一个软件包组.
//注意：@符号标志很重要,因为 Development 和 tools 中间有空格,所以要用单引号给引起来
ansible master -i hosts -m yum -a "name='@Development tools' state=present"
```

