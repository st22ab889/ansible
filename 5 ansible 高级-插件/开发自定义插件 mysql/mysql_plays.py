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
#   pip install pymysql
#   pip install mysqlclient
# 2.安装包后导入 pymysql 或者 MySQLdb, 注意: mysqlclient 包的模块名称为 MySQLdb。
#   这里使用"try"块来兼容两种mysql模块
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
# file.  This callback is an example of per hosts logging for those
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
