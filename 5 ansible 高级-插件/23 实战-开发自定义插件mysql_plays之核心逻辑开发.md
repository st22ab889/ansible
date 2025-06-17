1. 在 python 中获取当前登录系统的用户

```javascript
[root@localhost ~]# ipython
Python 2.7.5 (default, Nov 16 2020, 22:23:17) 
Type "copyright", "credits" or "license" for more information.

IPython 5.10.0 -- An enhanced Interactive Python.
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.

In [1]: import getpass

In [2]: getpass.getuser()
Out[2]: 'root'

In [3]: exit
[root@localhost ~]# su - aaron
Last login: Mon May  2 10:35:39 EDT 2022 on tty1
[aaron@localhost ~]$ python
Python 2.7.5 (default, Nov 16 2020, 22:23:17) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import getpass
>>> getpass.getuser()
'aaron'
>>> exit()
[aaron@localhost ~]$

```





2. 自定义插件mysql_plays之核心逻辑开发

```javascript
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
```



```javascript
参考资料：
自动化运维利器Ansible-扩展ansible
https://blog.csdn.net/qq_25518029/article/details/119678924

Python编码规范（PEP 8）
http://c.biancheng.net/view/4184.html
```

