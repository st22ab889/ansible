1. 区分 script 类型

如果执行的是shell脚本就不需要python解释器。

如果执行的是python脚本就需要python解释器。





2. 测试

```javascript
// 特别注意,这个脚本是放在 ansible管理机上
[root@centos7 ~]# echo  "touch /tmp/testfile" > test.sh
[root@centos7 ~]# cat test.sh 
touch /tmp/testfile
[root@centos7 ~]# ls /root/test.sh 
/root/test.sh

// 在管理节点上运行如下命令，最好是写脚本文件的绝对路径
// 这个命令失败，原因未知
[root@localhost ~]# ansible master -i hosts -m script -a "/root/test.sh"
192.168.32.100 | CHANGED => {
    "changed": true, 
    "rc": 0, 
    "stderr": "Shared connection to 192.168.32.100 closed.\r\n", 
    "stderr_lines": [
        "Shared connection to 192.168.32.100 closed."
    ], 
    "stdout": "", 
    "stdout_lines": []
}
// rc：0 表示执行命令的返回值是0，说明执行成功
// 如果执行命令有返回值就会放到 stdout 或 stdout_lines中,因为这里脚本里并没有输出，所以这里没有值

// 验证
[root@localhost ~]# ansible master -i hosts -m shell -a "ls -l /tmp"
192.168.32.100 | CHANGED | rc=0 >>
total 0
-rw-r--r--. 1 root root  0 Apr 14 12:47 a.conf
drwx------. 2 root root 41 Apr 18 13:33 ansible_command_payload_2ZGtcB
drwx------. 3 root root 17 Apr 18 11:03 systemd-private-b01674f1b56d43ada2528463f64bbf7c-chronyd.service-nSm2qV
-rw-r--r--. 1 root root  0 Apr 18 13:31 testfile

```



总结：

shell 和 script 类似，都可以执行脚本，却别在于script执行的脚本在ansible管理机上，而shell执行的脚本必须先放到目标节点上去，才能执行；另外shell执行可以使用环境变量，bash等，但是script只是执行脚本，不能带 bash。



参考资料：https://www.jianshu.com/p/d4c4597c7e46











