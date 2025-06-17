

```javascript
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
```





DOCUMENTATION 中最重要的是 options 块,这里定义了如下参数：

- mysql 主机

- mysql 端口（这个地方使用 type 定义了端口的值必须是一个 int 型）

- mysql 用户名

- mysql 密码

- 要使用的数据库

- 要使用的表