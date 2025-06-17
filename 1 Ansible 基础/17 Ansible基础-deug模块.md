1. deug模块主要用于调试时使用,通常的作用是将一个变量的值给打印出来。

![](images/4387A268B3084E2EA39A35B20280E4EFclipboard.png)



```javascript
// -e 可以传变量
[root@localhost ~]# ansible master -i hosts -m debug -a "var=role" -e "role=web"
192.168.32.100 | SUCCESS => {
    "role": "web"
}

// msg 可以格式化一段代码
[root@localhost ~]# ansible master -i hosts -m debug -a "msg='role is {{role}}'" -e "role=web"
192.168.32.100 | SUCCESS => {
    "msg": "role is web"
}
```



debug 在实际生产或测试当中会经常使用，debug 模块对调试还是比较方便。