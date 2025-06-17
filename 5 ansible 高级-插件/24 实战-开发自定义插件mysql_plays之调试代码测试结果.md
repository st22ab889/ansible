

1.  文件准备

1.1 hosts2

```javascript
[master]
192.168.32.100
[node]
# 这个主机实际上没有,实验效果需要
192.168.32.200
```



1.2 mysql_plays.py

```javascript
#coding:utf-8
# (C) 2012, Michael DeHaan, <michael.dehaan@gmail.com>
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: mysql_plays
    type: notification
    short_description: write playbook output to mysql
    version_added: historical
    description:
      - 写到 mysql 的 ansible 数据库的 playsresult 表中
    requirements:
     - Whitelist in configuration
     - 一个可以被访问的 MySQL 服务器实例
    options:
      mysql_host:
        version_added: '2.9'
        default: localhost
        description: MySQL 服务器的 IP 或者是可以被解析的主机名
        env:
          - name: ANSIBLE_MYSQL_HOST
        ini:
          - section: callback_mysql_plays
            key: mysql_host
      mysql_port:
        version_added: '2.9'
        default: 3306
        description: MySQL 服务器的监听端口
        env:
          - name: ANSIBLE_MYSQL_PORT
        ini:
          - section: callback_mysql_plays
            key: mysql_port
        type: int
      mysql_user:
        version_added: '2.9'
        default: ansible
        description: MySQL 服务器的用户
        env:
          - name: ANSIBLE_MYSQL_USER
        ini:
          - section: callback_mysql_plays
            key: mysql_user
      mysql_password:
        version_added: '2.9'
        default: ansible
        description: MySQL 服务器的用户密码
        env:
          - name: ANSIBLE_MYSQL_PASSWORD
        ini:
          - section: callback_mysql_plays
            key: mysql_password
      mysql_db:
        version_added: '2.9'
        default: ansible
        description: MySQL 服务器的库名
        env:
          - name: ANSIBLE_MYSQL_DB
        ini:
          - section: callback_mysql_plays
            key: mysql_db
      mysql_table:
        version_added: '2.9'
        default: playsresult
        description: MySQL 服务器的表名称
        env:
          - name: ANSIBLE_MYSQL_TABLE
        ini:
          - section: callback_mysql_plays
            key: mysql_table
'''

import os
import time
import json
import getpass

from ansible.utils.path import makedirs_safe
from ansible.module_utils._text import to_bytes
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback import CallbackBase
# to_native 方法可以用转换输出(比如抛出异常类的输出),
from ansible.module_utils._text import to_native

# 1.首先安装 Python 的 pymysql 包或者 mysqlclient 包,安装包命令如下:
#   pip install pymysql
#   pip install mysqlclient
# 2.安装包后导入 pymysql 或者 MySQLdb, 注意: mysqlclient 包的模块名称为 MySQLdb。
#   这里使用"try"块来兼容两种mysql模块
from ansible.errors import AnsibleError
try:
    import pymysql as mysqldb
    pwd = "password"
    db = "database"
except ImportError:
    try:
        import MySQLdb as mysqldb
        pwd = "passwd"
        db = "db"
    except ImportError as e:
        # 将其他异常包装到错误消息中时，应始终使用Ansible 的函数 to_native 来确保跨Python版本的字符串兼容性
        raise AnsibleError("找不到 pymysql 或者 MySQLdb 模块。" + "=================>>" + to_native(e))

# NOTE: in Ansible 1.2 or later general logging is available without
# this plugin, just set ANSIBLE_LOG_PATH as an environment variable
# or log_path in the DEFAULTS section of your ansible configuration
# file.  This callback is an example of per hosts logging for those
# that want it.


class CallbackModule(CallbackBase):
    """
    logs playbook results, per host, in /var/log/ansible/hosts
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'mysql_plays'
    # CALLBACK_NEEDS_WHITELIST 设为 true, 表示插件需要添加到 ansible.cfg 文件中的白名单参数里面才生效
    CALLBACK_NEEDS_WHITELIST = True

    TIME_FORMAT = "%b %d %Y %H:%M:%S"
    MSG_FORMAT = "%(now)s - %(category)s - %(data)s\n\n"

    def __init__(self):

        super(CallbackModule, self).__init__()

    # set_options 函数由 ansible 自动回调
    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.mysql_host = self.get_option("mysql_host")
        self.mysql_port = self.get_option("mysql_port")
        self.mysql_user = self.get_option("mysql_user")
        self.mysql_password = self.get_option("mysql_password")
        self.mysql_db = self.get_option("mysql_db")
        self.mysql_table = self.get_option("mysql_table")
        # 查看是哪个用户运行的ansible命令(也就是当前登录系统的用户)
        self.user = getpass.getuser()

    # _开头的函数表示仅仅给内部自己调用
    def _mysql(self):
      """
      连接 MySQL 数据库, 返回游标对象(执行sql的对象)和db数据库对象(数据库连接对象)
      """

      # 关键字参数可以用字典的方式传值
      conn_param = {
        "host": self.mysql_host,
        "port": self.mysql_port,
        "user": self.mysql_user,
        pwd: self.mysql_password,
        db: self.mysql_db
      }
      try:
          conn = mysqldb.connect(**conn_param)
      except Exception as e:
          raise AnsibleError("%s" % to_native(e))
      
      cursor = conn.cursor()
      return conn, cursor

    def _execute_mysql(self, host, category, data):
        if isinstance(data, MutableMapping):
            if '_ansible_verbose_override' in data:
                # avoid logging extraneous data
                data = 'omitted'
            else:
                data = data.copy()
                invocation = data.pop('invocation', None)
                data = json.dumps(data, cls=AnsibleJSONEncoder)
                if invocation is not None:
                    data = json.dumps(invocation) + " => %s " % data

        sql = """
              insert into {}(host, user, category, result
              ) values(%s, %s, %s, %s)
              """.format(self.mysql_table)

        conn, cursor = self._mysql()

        try:
            cursor.execute(sql, (host, self.user, category, data))
            conn.commit()
        except Exception as e:
            raise AnsibleError("%s" % to_native(e))
        finally:  
            cursor.close()
            conn.close()
        
    def runner_on_failed(self, host, res, ignore_errors=False):
        self._execute_mysql(host, 'FAILED', res)

    def runner_on_ok(self, host, res):
        self._execute_mysql(host, 'OK', res)

    def runner_on_skipped(self, host, item=None):
        self._execute_mysql(host, 'SKIPPED', '...')

    def runner_on_unreachable(self, host, res):
        self._execute_mysql(host, 'UNREACHABLE', res)

    def runner_on_async_failed(self, host, res, jid):
        self._execute_mysql(host, 'ASYNC_FAILED', res)

    def playbook_on_import_for_host(self, host, imported_file):
        self._execute_mysql(host, 'IMPORTED', imported_file)

    def playbook_on_not_import_for_host(self, host, missing_file):
        self._execute_mysql(host, 'NOTIMPORTED', missing_file)

```

```javascript
python 开发规范,在文件末尾要空一行
```





2.  将自定义插件 mysql_plays.py 放到对应目录

```javascript
// 以下两个目录都可以放置自定义插件文件:
/usr/share/ansible/plugins/callback/
.ansible/plugins/callback/
//注意:
// ".ansible"是个隐藏目录,这个目录在要运行ansible命令的这个用户的家目录下面
// 比如是root用户运行ansible命令,这个目录的路径为 /root/.ansible/plugins/callback/
```



```javascript
// 这里把 mysql_plays.py 放到".ansible/plugins/callback/"目录,完整路径为:
/root/.ansible/plugins/callback/mysql_plays.py
```





 3.  修改 ansible 配置文件

```javascript
# 修改 "/etc/ansible/ansible.cfg" 文件, 如下：
callback_whitelist = timer, log_plays, mysql_plays
bin_ansible_callbacks = True

[callback_log_plays]
log_folder = /tmp/ansible/hosts/

# 如果下面的参数没有指定,将会使用"mysql_plays.py"文件中定义的默认参数
[callback_mysql_plays]
mysql_host= 192.168.32.99
mysql_port = 3306
mysql_user = ansible
mysql_password = ansible
mysql_db = ansible
mysql_table = playsresult

```





4. 查看帮助文档

```javascript
[root@localhost ~]# ansible-doc -t callback -l | grep mysql
mysql_plays          write playbook output to mysql

[root@localhost ~]# ansible-doc -t callback mysql_plays
> MYSQL_PLAYS    (/root/.ansible/plugins/callback/mysql_plays.py)

        写到 mysql 的 ansible 数据库的 playsresult 表中

  * This module is maintained by The Ansible Community
OPTIONS (= is mandatory):

- mysql_db
        MySQL 服务器的库名
        [Default: ansible]
        set_via:
          env:
          - name: ANSIBLE_MYSQL_DB
          ini:
          - key: mysql_db
            section: callback_mysql_plays
        
        version_added: 2.9

- mysql_host
        MySQL 服务器的 IP 或者是可以被解析的主机名
        [Default: localhost]
        set_via:
          env:
          - name: ANSIBLE_MYSQL_HOST
          ini:
          - key: mysql_host
            section: callback_mysql_plays
        
        version_added: 2.9

- mysql_password
        MySQL 服务器的用户密码
        [Default: ansible]
        set_via:
          env:
          - name: ANSIBLE_MYSQL_PASSWORD
          ini:
          - key: mysql_password
            section: callback_mysql_plays
        
        version_added: 2.9

- mysql_port
        MySQL 服务器的监听端口
        [Default: 3306]
        set_via:
          env:
          - name: ANSIBLE_MYSQL_PORT
          ini:
          - key: mysql_port
            section: callback_mysql_plays
        
        type: int
        version_added: 2.9

- mysql_table
        MySQL 服务器的表名称
        [Default: playsresult]
        set_via:
          env:
          - name: ANSIBLE_MYSQL_TABLE
          ini:
          - key: mysql_table
            section: callback_mysql_plays
        
        version_added: 2.9

- mysql_user
        MySQL 服务器的用户
        [Default: ansible]
        set_via:
          env:
          - name: ANSIBLE_MYSQL_USER
          ini:
          - key: mysql_user
            section: callback_mysql_plays
        
        version_added: 2.9


REQUIREMENTS:  Whitelist in configuration, 一个可以被访问的 MySQL 服务器实例

        METADATA:
          status:
          - preview
          supported_by: community
        
TYPE: notification

// 运行上面命令如果显示中文乱码,解决方法是设置linux 默认编码为中文,如下:
//   export LC_ALL=zh_CN.utf8
```





5. 运行 playbook，测试 mysql_plays 插件

```javascript
// 运行 ansible 命令
[root@localhost ~]# ansible all -i hosts2 -m ping
192.168.32.100 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": false, 
    "ping": "pong"
}
[WARNING]: Unhandled error in Python interpreter discovery for host 192.168.32.200: Failed to connect to the host via ssh: ssh: connect to host
192.168.32.200 port 22: No route to host
192.168.32.200 | UNREACHABLE! => {
    "changed": false, 
    "msg": "Data could not be sent to remote host \"192.168.32.200\". Make sure this host can be reached over ssh: ssh: connect to host 192.168.32.200 port 22: No route to host\r\n", 
    "unreachable": true
}
Playbook run took 0 days, 0 hours, 0 minutes, 6 seconds
[root@localhost ~]#

```



```javascript
// 验证 mysql_plays 插件, 进入到数据库中查看：
[root@localhost ~]# mysql -u root -p
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 10
Server version: 5.7.38 MySQL Community Server (GPL)

Copyright (c) 2000, 2022, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> use ansible
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> select * from playsresult;
+----+------+----------------+-------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
| id | user | host           | category    | result                                                                                                                                                                                                                     | create_time         |
+----+------+----------------+-------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
|  1 | root | 192.168.32.100 | OK          | {"module_args": {"data": "pong"}} => {"changed": false, "ping": "pong", "_ansible_no_log": false, "ansible_facts": {"discovered_interpreter_python": "/usr/bin/python"}}                                                   | 2022-05-15 13:36:39 |
|  2 | root | 192.168.32.200 | UNREACHABLE | {"msg": "Data could not be sent to remote host \"192.168.32.200\". Make sure this host can be reached over ssh: ssh: connect to host 192.168.32.200 port 22: No route to host\r\n", "unreachable": true, "changed": false} | 2022-05-15 13:36:44 |
+----+------+----------------+-------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
2 rows in set (0.01 sec)

mysql> select * from playsresult\G
*************************** 1. row ***************************
         id: 1
       user: root
       host: 192.168.32.100
   category: OK
     result: {"module_args": {"data": "pong"}} => {"changed": false, "ping": "pong", "_ansible_no_log": false, "ansible_facts": {"discovered_interpreter_python": "/usr/bin/python"}} 
create_time: 2022-05-15 13:36:39
*************************** 2. row ***************************
         id: 2
       user: root
       host: 192.168.32.200
   category: UNREACHABLE
     result: {"msg": "Data could not be sent to remote host \"192.168.32.200\". Make sure this host can be reached over ssh: ssh: connect to host 192.168.32.200 port 22: No route to host\r\n", "unreachable": true, "changed": false}
create_time: 2022-05-15 13:36:44
2 rows in set (0.00 sec)

mysql> exit
Bye
[root@localhost ~]#
```



```javascript
// 验证 log_folder 插件, 查看"/tmp/ansible/hosts/"目录中的 log 文件:
[root@localhost ~]# ls /tmp/ansible/hosts/
192.168.32.100  192.168.32.200

[root@localhost ~]# cat /tmp/ansible/hosts/192.168.32.100 
May 15 2022 13:36:39 - OK - {"module_args": {"data": "pong"}} => {"changed": false, "ping": "pong", "_ansible_no_log": false, "ansible_facts": {"discovered_interpreter_python": "/usr/bin/python"}} 

[root@localhost ~]# cat /tmp/ansible/hosts/192.168.32.200 
May 15 2022 13:36:44 - UNREACHABLE - {"msg": "Data could not be sent to remote host \"192.168.32.200\". Make sure this host can be reached over ssh: ssh: connect to host 192.168.32.200 port 22: No route to host\r\n", "unreachable": true, "changed": false}

[root@localhost ~]# 
```





6. 注意点

6.1 为什么"mysql_plays.py"文件第一行是"#coding:utf-8"

因为 centos7 的 Python 版本默认是 Python 2.7，也就是说 Python 默认用的解释器是 2.7， Python2 默认不支持字符串，只支持 ASCII 码，但是用 ASCII 码解释不了中文，不管是注释里面的中文还是代码中的中文都不支持。所以加上这一句是告诉 python 解释器用 utf-8 解释中文。

```javascript
// 如果在"mysql_plays.py"文件中第一行没有加"#coding:utf-8"
// 在运行下面命令时就会出现警告, 提示有字符问题
ansible all -i hosts2 -m ping
```



6.2 ansible 的插件可以添加多个

```javascript
// 如下：
# enable callback plugins, they can output to stdout but cannot be 'stdout' type.
callback_whitelist = timer, log_plays, mysql_plays

// 注意上面的注释：意思是可以输出到标准输出,但是这里不能是标准输出这种(回调)类型
// 标准输出是通过"stdout_callback"这个字段定义的,如下:
# change the default callback, you can only have one 'stdout' type  enabled at a time.
#stdout_callback = skippy
#stdout_callback = json
```



6.3 ansible 的 AdHoc 命令要使用插件功能，需要单独开启，如下：

```javascript
# by default callbacks are not loaded for /bin/ansible, enable this if you
# want, for example, a notification or logging callback to also apply to
# /bin/ansible runs
bin_ansible_callbacks = True

```



6.4 扩展

```javascript
"docker inspect [容器名称]"命令表示获取容器/镜像的元数据(比如IP地址等)。
"docker inspect ansible" 表示获取 ansible 这个容器的元数据。
```