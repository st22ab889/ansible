1. 安装 Redis，redis 可以在本机或其他机器上安装，这里就安装在 ansible 所在的主机上

```javascript
[root@localhost ~]# yum install redis
// ......

[root@localhost ~]# systemctl start redis
// ......

// 开机启动redis
[root@localhost ~]# systemctl enable redis
Created symlink from /etc/systemd/system/multi-user.target.wants/redis.service to /usr/lib/systemd/system/redis.service.

[root@localhost ~]# systemctl status redis
● redis.service - Redis persistent key-value database
   Loaded: loaded (/usr/lib/systemd/system/redis.service; disabled; vendor preset: disabled)
  Drop-In: /etc/systemd/system/redis.service.d
           └─limit.conf
   Active: active (running) since Fri 2022-05-06 03:34:18 EDT; 21s ago
 Main PID: 1821 (redis-server)
   CGroup: /system.slice/redis.service
           └─1821 /usr/bin/redis-server 127.0.0.1:6379

May 06 03:34:18 localhost.localdomain systemd[1]: Starting Redis persistent key-value database...
May 06 03:34:18 localhost.localdomain systemd[1]: Started Redis persistent key-value database.

[root@localhost ~]# redis-cli
127.0.0.1:6379> info
//......
127.0.0.1:6379> exit
[root@localhost ~]#
```



使用 redis-cli 连接远程：

```javascript
[root@localhost ~]# hostname -i
::1 127.0.0.1 192.168.32.99
[root@localhost ~]# redis-cli -h 192.168.32.99 -p 6379
Could not connect to Redis at 192.168.32.99:6379: Connection refused
Could not connect to Redis at 192.168.32.99:6379: Connection refused
// 连接失败原因是：yum安装redis，默认情况下只监听到 127.0.0.1 这个主机

// 修改 /etc/redis.conf 
vi /etc/redis.conf
# bind 127.0.0.1

// 说明:
//   如果绑定的是本地地址, 设置为 bind 192.168.32.99
//	  如果绑定的是本地机器任意的网卡地址, 设置为 bind 0.0.0.0

// 所以直接修改为如下：
bind 0.0.0.0

[root@localhost ~]# systemctl restart redis

// 再次使用 IP 连接远程主机(这里相当于是模拟远程),命令中不指定端口,则默认使用 6379
[root@localhost ~]# redis-cli -h 192.168.32.99
192.168.32.99:6379> exit
[root@localhost ~]#
```





2. 修改 ansible 配置 

2.1 修改 ansible 配置

```javascript
// 修改 /etc/ansible/ansible.cfg 中相关配置为如下：
gathering = smart
fact_caching = redis
fact_caching_connection=192.168.32.99:6379:0
fact_caching_timeout = 600

// 说明：
// "192.168.32.99:6379:0"后面的0表示: redis有16个数据库, 默认使用第一个数据库
```



```javascript
# cat checkhosts-two.yml
- hosts: all
  #开启 facts,如果设置为 no 或 false 表示关闭获取 facts 变量
  #gather_facts: no
  tasks:
    - name: check hosts
      ping:
    - name: debug
      debug:
      #var: ansbile_distribution
      var: ansible_facts
```



2.2 安装 'redis' python module

```javascript
[root@localhost ~]# ansible-playbook -i hosts checkhosts-two.yml --limit master
[WARNING]: The 'redis' python module (version 2.4.5 or newer) is required for the redis fact cache, 'pip install redis'
// ......


// 从上面的 WARNING 可以看出,要安装 redis 的 python module
[root@localhost ~]# pip install redis
-bash: pip: command not found


// 要先安装 pip, 因为 yum 安装的这个 python 是系统自带的, 系统自带的没有pip命令
[root@localhost ~]# which pip
/usr/bin/which: no pip in (/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin)
// 看下pip是哪个软件安装的
[root@localhost ~]# rpm -qf /usr/bin/pip
error: file /usr/bin/pip: No such file or directory
[root@localhost ~]# yum install python2-pip
Loaded plugins: fastestmirror
// ......
[root@localhost ~]# pip
// 如果有返回信息,说明 pip 安装成功......


// 安装 pip 后, 再次安装 redis 的 python module
[root@localhost ~]# pip install redis==3.4.0
Collecting redis==3.4.0
  Downloading https://files.pythonhosted.org/packages/b1/2d/7b9d942b6753433f8b77a1cb1fc2fb613c946b07439d39ab631486384fa0/redis-3.4.0-py2.py3-none-any.whl (70kB)
    100% |████████████████████████████████| 71kB 298kB/s 
Installing collected packages: redis
Successfully installed redis-3.4.0
You are using pip version 8.1.2, however version 22.0.4 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.


// 从以上信息可以知道安装redis 的 python module, 但是提示升级 pip
// 但是升级失败,原因是版本升级跨度较大，低级版本无法直接升级到高级版本
[root@localhost ~]# pip install --upgrade pip
//......
Command "python setup.py egg_info" failed with error code 1 in /tmp/pip-build-7_tXdb/pip/
You are using pip version 8.1.2, however version 22.0.4 is available.
You should consider upgrading via the 'pip install --upgrade pip' command

```



```javascript
// 官方衔接,包含各种 Python 库(功能模块), 比如 pip、redis、mysql 等
PyPI · The Python Package Index:  https://pypi.org/
```





2.3  验证 Facts缓存到 Redis

```javascript
// 首次运行,从远程主机获取 facts
[root@localhost ~]#  ansible-playbook -i hosts checkhosts-two.yml --limit master
// ......

// 进入到 redis 中验证
[root@localhost ~]# redis-cli -h 192.168.32.99
192.168.32.99:6379> keys *
1) "ansible_facts192.168.32.100"
2) "ansible_cache_keys"
192.168.32.99:6379> type ansible_facts192.168.32.100
string
192.168.32.99:6379> get ansible_facts192.168.32.100
//facts 数据......
192.168.32.99:6379> ttl ansible_facts192.168.32.100
(integer) 536
192.168.32.99:6379> ttl ansible_facts192.168.32.100
(integer) 533
192.168.32.99:6379> exit
[root@localhost ~]#


```



总结：

-  只有 redis 里面的缓存时间到期了，运行命令时才会再次从远程主机获取 facts 信息。

- 工作中可以使用缓存进一步对 facts 变量进行管理，并且缓存 facts 变量也能加速 playbook 的执行。





3. 问题解决

3.1 "pip install redis"失败,

问题原因：是默认安装的最新版本 redis 模块, 但是 pip 是老版本, 所以并不能识别到新版本模块中的源代码中的一些关键字或语法等。

解决方法：安装低版本的 redis 模块。

```javascript
[root@localhost ~]#  pip install redis
Collecting redis
  Using cached https://files.pythonhosted.org/packages/31/4c/7ee8f6319c26370f636bce7b4ad2ab9d76ed102243c91d853e7e144621d9/redis-4.2.2.tar.gz
    Complete output from command python setup.py egg_info:
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "/tmp/pip-build-q7L6QK/redis/setup.py", line 21, in <module>
        "redis.commands.graph",
    TypeError: find_packages() got an unexpected keyword argument 'include'
    
    ----------------------------------------
Command "python setup.py egg_info" failed with error code 1 in /tmp/pip-build-q7L6QK/redis/
You are using pip version 8.1.2, however version 22.0.4 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.


// 在如下衔接可以查看到 redis 模块的各个历史版本
// https://pypi.org/project/redis/3.4.0/#history


// 指定安装 3.4.0 版本的 redis
[root@localhost ~]# pip install redis==3.4.0
Collecting redis==3.4.0
  Downloading https://files.pythonhosted.org/packages/b1/2d/7b9d942b6753433f8b77a1cb1fc2fb613c946b07439d39ab631486384fa0/redis-3.4.0-py2.py3-none-any.whl (70kB)
    100% |████████████████████████████████| 71kB 298kB/s 
Installing collected packages: redis
Successfully installed redis-3.4.0
You are using pip version 8.1.2, however version 22.0.4 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.

```





3.2 卸载 pip 后，再安装 pip 不成功。

问题原因：没有卸载 pip 的 rpm 包

解决方法：卸载 pip 的 rpm 包，然后再重新安装 pip

```javascript
// 卸载 pip
[root@localhost ~]# pip uninstall pip
//......

// 重新安装 pip，但是失败
[root@localhost ~]# yum install python2-pip
Loaded plugins: fastestmirror
Loading mirror speeds from cached hostfile
 * base: mirrors.dgut.edu.cn
 * epel: hkg.mirror.rackspace.com
 * extras: mirrors.dgut.edu.cn
 * updates: mirrors.dgut.edu.cn
Package python2-pip-8.1.2-14.el7.noarch already installed and latest version
Nothing to do
[root@localhost ~]# pip
-bash: /usr/bin/pip: No such file or director

[root@localhost ~]# rpm -qf /usr/bin/pip
python2-pip-8.1.2-14.el7.noarch
// 卸载 pip 的 rpm 包
[root@localhost ~]# rpm -e python2-pip-8.1.2-14.el7.noarch
warning: file /usr/lib/python2.7/site-packages/pip/wheel.pyo: remove failed: No such file or directory
//.....

// 再次重新安装 pip
[root@localhost ~]# yum install python2-pip
Loaded plugins: fastestmirror
Loading mirror speeds from cached hostfile
// ......

// 安装后验证
[root@localhost ~]# pip

Usage:   
  pip <command> [options]
// ......  
```

