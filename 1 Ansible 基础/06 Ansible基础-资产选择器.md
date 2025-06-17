1. 资产选择器 PATTERN

```javascript
// 基本语法格式
ansible [PATTERN] -i [inventory] -m [module] -a [argument]
```





2. 基于上节的 inventory.ini 资产文件选择资产

```javascript
// 选择一台或几台主机

[root@localhost ~]# ansible test03.aaron.com -i inventory.ini --list-hosts
  hosts (1):
    test03.aaron.com
// 这里这里的IP，inventory.ini 里面是 IP 就写 IP，是域名就写域名。
// 不要根据本机的 hosts 文件去写 ip 对应的域名, 这里根 hosts 文件没关系    
[root@localhost ~]# ansible 1.1.1.1,2.2.2.2 -i inventory.ini --list-hosts
  hosts (2):
    1.1.1.1
    2.2.2.2

// 选择一组资产
[root@localhost ~]# ansible web_servers -i inventory.ini --list-hosts
  hosts (3):
    192.168.1.2
    192.168.1.3
    192.168.1.5

// 使用 * 匹配
[root@localhost ~]# ansible 3.3.3.1* -i inventory.ini --list-hosts
  hosts (7):
    3.3.3.12
    3.3.3.10
    3.3.3.11
    3.3.3.13
    3.3.3.14
    3.3.3.15
    3.3.3.1
```



```javascript
// 使用“:”求并集,求交集会自动去重
// 注意选择资产加上单引号,这里不加也可以,但是求交集不加单引号就会报错,所以统一加上
[root@localhost ~]# ansible 'web_servers:db_servers' -i inventory.ini --list-hosts
  hosts (5):
    192.168.1.2
    192.168.1.3
    192.168.1.5
    192.168.2.2
    192.168.2.3

    
// 使用“:&”求交集
[root@localhost ~]# ansible 'web_servers:&db_servers' -i inventory.ini --list-hosts
  hosts (1):
    192.168.1.5

// 使用":!"排除. 下面命令表示在 web_servers 组,不在 ab_servers 组,有前后顺序
[root@localhost ~]# ansible 'web_servers:!db_servers' -i inventory.ini --list-hosts
  hosts (2):
    192.168.1.2
    192.168.1.3
```

