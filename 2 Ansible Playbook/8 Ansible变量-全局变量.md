1. 全局变量

使用 ansible 或使用 ansible-playbook 时,手动通过 -e 参数传递给 ansible 的变量。



通过 ansible 或 ansible-playbook 的 help 帮助,可以获取具体格式使用方式: 

```javascript
[root@localhost ~]# ansible -h | grep var
                        path for many features including roles/ group_vars/
  -e EXTRA_VARS, --extra-vars EXTRA_VARS
                        set additional variables as key=value or YAML/JSON, if
                        
[root@localhost ~]# ansible-playbook -h | grep var
  -e EXTRA_VARS, --extra-vars EXTRA_VARS
                        set additional variables as key=value or YAML/JSON, if                        
```





2. 传递普通的 key=value 的形式

```javascript
[root@localhost ~]# ansible all -i localhost, -m debug -a "msg='my key is {{key}}'" -e "key=PrivateKey"
localhost | SUCCESS => {
    "msg": "my key is PrivateKey"
}

// localhost 表示连接本机, 这里只是本地测试(调试)
```





3. 传递一个 YAML/JSON 的形式

```javascript
//注意：不管是YAML还是JSON, 最终格式都一定是一个字典
# var.yml
---
name: apple
type: fruit
```



```javascript
[root@localhost ~]# ansible all -i localhost, -m debug -a "msg='name is {{name}},type is {{type}}'" -e @var.yml
[WARNING]: Found variable using reserved name: name
localhost | SUCCESS => {
    "msg": "name is apple,type is fruit"
}

// 可以发现这里出现了WARNING, 原因是这里的 name 和 ansible 的yaml属性冲突

```

