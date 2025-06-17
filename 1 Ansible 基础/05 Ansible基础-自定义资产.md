1. 资产概念

- 静态资产(Inventory)指的是在文件中指定的主机和组，

- 动态资产(Inventory)指通过外部脚本获取主机列表，并按照 ansible 所要求的格式返回给 ansilbe 命令。这个脚本中可以写一些逻辑，比如从数据库中获取主机列表。

- 资产文件有 ini 和 yaml 两种风格，通常会写为 ini 这种风格，因为比较简洁。



2. ansible 自带的资产文件示例

```javascript
// ansible 自带的资产文件示例
[root@localhost ~]# cat /etc/ansible/hosts 
# This is the default ansible 'hosts' file.
#
# It should live in /etc/ansible/hosts
#
#   - Comments begin with the '#' character
#   - Blank lines are ignored
#   - Groups of hosts are delimited by [header] elements
#   - You can enter hostnames or ip addresses
#   - A hostname/ip can be a member of multiple groups

# Ex 1: Ungrouped hosts, specify before any group headers.

## green.example.com
## blue.example.com
## 192.168.100.1
## 192.168.100.10

# Ex 2: A collection of hosts belonging to the 'webservers' group

## [webservers]
## alpha.example.org
## beta.example.org
## 192.168.1.100
## 192.168.1.110

# If you have multiple hosts following a pattern you can specify
# them like this:

## www[001:006].example.com

# Ex 3: A collection of database servers in the 'dbservers' group

## [dbservers]
## 
## db01.intranet.mydomain.net
## db02.intranet.mydomain.net
## 10.25.1.56
## 10.25.1.57

# Here's another example of host ranges, this time there are no
# leading 0s:

## db-[99:101]-node.example.com

```



3. ansible 自定义资产示例

```javascript
// 在当前目录下创建 inventory.ini 文件 
[root@localhost ~]# vi inventory.ini
1.1.1.1
2.2.2.2
3.3.3.[1:15]
test01.aaron.com
test02.aaron.com
test[02:09].aaron.com

[web_servers]
192.168.1.2
192.168.1.3
192.168.1.5

[db_servers]
192.168.2.2
192.168.2.3
192.168.1.5

# children 是固定写法,表示子组.这里表示 web_servers 和 db_servers 都属于 all_servers,相当于并集
# children 可以自动去重
[all_servers]
[all_servers:children]
web_servers
db_servers

[root@localhost ~]# ls
anaconda-ks.cfg  inventory.ini
```



```javascript
// 列出所有资产并自动去重
[root@localhost ~]# ansible all -i inventory.ini --list-hosts
  hosts (32):
    nventory.ini
    1.1.1.1
    // 省略......
    3.3.3.15
    test01.aaron.com
    test02.aaron.com
    // 省略......
    192.168.2.3

// 列出某个组的资产     
[root@localhost ~]# ansible all_servers -i inventory.ini --list-hosts
  hosts (5):
    192.168.1.2
    192.168.1.3
    192.168.1.5
    192.168.2.2
    192.168.2.3
```

