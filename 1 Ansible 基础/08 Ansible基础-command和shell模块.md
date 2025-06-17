1. 准备 ansible 使用到的 hosts 文件，hosts 文件中是真实的被管理节点

```javascript
[root@localhost ~]# vi hosts
[master]
192.168.32.100
[node]
192.168.32.101

[root@localhost ~]# pwd
/root

[root@localhost ~]# ls
anaconda-ks.cfg  hosts  inventory.ini
```





2. command 和 shell 模块

```javascript
// 默认会用command 模块运行"echo 'hello'"
[root@localhost ~]# ansible all -i hosts -a "echo 'hello'"
192.168.32.100 | CHANGED | rc=0 >>
hello
192.168.32.101 | CHANGED | rc=0 >>
hello

[root@localhost ~]# ansible all -i hosts -a "hostname -i"
192.168.32.100 | CHANGED | rc=0 >>
127.0.0.1 192.168.32.100
192.168.32.101 | CHANGED | rc=0 >>
127.0.0.1 192.168.32.101

[root@localhost ~]# ansible all -i hosts -m shell -a "hostname -i"
192.168.32.101 | CHANGED | rc=0 >>
127.0.0.1 192.168.32.101
192.168.32.100 | CHANGED | rc=0 >>
127.0.0.1 192.168.32.100

```



command 和 command 两个模块区别：

- command 模块无法执行 SHELL 的内置命令和特性

- shell 模块可以执行 SHELL 的内置命令和特性(比如管道、输入、输出、重定向等)。

```javascript
[root@localhost ~]# ansible all -i hosts -m shell -a "echo 'hello' | grep -o 'e'"
192.168.32.101 | CHANGED | rc=0 >>
e
192.168.32.100 | CHANGED | rc=0 >>
e

[root@localhost ~]# ansible all -i hosts -a "echo 'hello' | grep -o 'e'"
192.168.32.101 | CHANGED | rc=0 >>
hello | grep -o e
192.168.32.100 | CHANGED | rc=0 >>
hello | grep -o e
```

