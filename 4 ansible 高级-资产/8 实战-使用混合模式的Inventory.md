1. 混合模式的Inventory

使用多个 Inventory 的原因是，当服务器分的环境比较复杂比较多的情况下，使用一个资产清单就特别不好维护。这时就可以根据环境、机器不同用途等分为多个 Inventory 文件，ansible 支持多个资产文件，最终会把多个资产文件合并为一个，然后给 ansible-playbook 执行。使用多个 Inventory 有两种方式：



方式1:  直接在命令行种指定多个资源文件，例如：

```javascript
ansible-playbook all -i 1.yml 2.yml 3.yml 
```



方式2:  把所有资产文件放入到一个文件夹中，例如：

```javascript
// 把 1.yml 2.yml 3.yml 放入一个名为 inventory 的文件夹中,在命令中指定文件夹名称
// 资产文件的扩展名可以为 ".yaml"、".yml"、".json", 或者没有扩展名 
ansible-playbook all -i inventory/ 
```





2. 插件和动态脚本

- 资产文件支持插件, 这个插件必须是 python 写的。

- 资产文件可以是个动态脚本(脚本在执行时要改成可执行权限)，这个脚本必须返回一个 json 格式数据，编写脚本没有语言限制，可以是python、shell、java、go等语言(只要能运行)，按照 ansible 规定的 json 格式数据返回就行。





3. 多个 Inventory 使用示例

指定多个资产文件可能存在变量(同名的变量)被覆盖的情况，变量覆盖是按目录中文件的顺序(文件名第一个字符在 ASCII 编码的顺序进行排序)，最后执行的那个变量会最后生效，前面的变量都会被覆盖。既然有顺序那就可以控制变量的优先级，比如文件名使用数字作为前缀进行控制。



示例1：资产文件夹中只包含静态资产文件

```javascript
[root@localhost ~]# tree inventory-var/
inventory-var/
├── 01-static
└── 02-static

0 directories, 2 files
```



```javascript
# cat 01-static
[master]
192.168.32.100
#192.168.32.[100-110] # 也可以用这种方式连续指定多台主机

[allHosts:children]
master

[allHosts:vars]
name=static-01-vars
---------------------------------文件分割线---------------------------------
# cat 02-static
[node]
192.168.32.101

[allHosts:children]
node

[allHosts:vars]
name=static-02-vars
```



```javascript
[root@localhost ~]# ansible all -i inventory-var/ -m debug -a "var=name"
192.168.32.100 | SUCCESS => {
    "name": "static-02-vars"
}
192.168.32.101 | SUCCESS => {
    "name": "static-02-vars"
}

```

结论： “02-static”这个资产文件里面定义的变量生效！



示例2：资产文件夹中只包含静态资产文件以及组变量文件

```javascript
[root@localhost ~]# tree inventory-var-group/
inventory-var-group/
├── 01-static
├── 02-static
└── group_vars
    └── all.yml

1 directory, 3 files
```

注意： group_vars 这个文件夹的名称时固定的！



```javascript
# cat 01-static
[master]
192.168.32.100
#192.168.32.[100-110] # 也可以用这种方式连续指定多台主机

[allHosts:children]
master

[allHosts:vars]
name=static-01-vars
---------------------------------文件分割线---------------------------------
# cat 02-static
[node]
192.168.32.101

[allHosts:children]
node

[allHosts:vars]
name=static-02-vars
---------------------------------文件分割线---------------------------------
# cat all.yml
name: varInAll
```



```javascript
[root@localhost ~]# ansible all -i inventory-var-group/ -m debug -a "var=name"
192.168.32.100 | SUCCESS => {
    "name": "varInAll"
}
192.168.32.101 | SUCCESS => {
    "name": "varInAll"
}

```

结论： “all.yml”这个变量文件里面定义的变量生效，说明对所有组定义的变量都生效。



资产文件夹也可以配置在 ansible 的配置文件中：

```javascript
# /etc/ansible/ansible.cfg 中的 inventory 属性,例如：
inventory = /root/inventory-var-group/
```



总结：

使用多个 inventory，其实就是混合了静态资产文件、插件、脚本，比如可以写个插件对某些云(比如阿里云、腾讯云等)，也可以用一个脚本从 CMD 或监控系统等获取主机，还可以写多个静态文件，把生产环境和测试环境分开，例如：

```javascript
[root@localhost ~]# tree inventory/
inventory/
├── 01-pro
└── 02-dev
```

