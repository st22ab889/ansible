1. 缓存 Facts

如果不希望每次执行 playbook 都去获取 facts，但还是希望使用 ansible_facts 变量，这时就可以把 Facts 缓存到本机文件或 redis 中( redis 可以在本机或其他机器上安装)。

```javascript
# cat checkhosts-two.yml
- hosts: all
  #开启 facts,如果设置为 no 或 false 表示关闭获取 facts 变量
  #gather_facts: no
  tasks:
    - name: check hosts
      ping:
    - name: debug
      debug:
      #var: ansbile_distribution
      var: ansible_facts
```





2. 将Facts缓存到 JSONFILE

修改配置如下：

```javascript
vi /etc/ansible/ansible.cfg
#gathering = implicit
#fact_caching = memory
#fact_caching_connection=/tmp
//1. gathering 表示获取 fact 的策略,有以下几种:
//     smart - 默认收集，但如果已经收集则不重新收集
//     implicit - 默认收集，用gather_facts关闭：False, 这个时默认策略
//     explicit - 默认情况下不收集，必须指定 gather_facts: True

// 2. fact_caching 表示把 fact 的持久化形式, 有以下几个值:
//     memory
//     jsonfile
//     redis

// 3. fact_caching_connection 表示把持久化的 fact 文件放在什么地方。
//      注意：不要随意设置一个目录，这样有时候会被删掉。
//            比如 /tmp 目录, 可能有些计划任务每隔一段时间就会清理。

配置文件中改为如下：
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /dev/shm/ansible_facts_cache/
fact_caching_timeout = 60

// 说明：
//  "/dev/shm/" 是系统目录, 自动就存在且必须有的,ansible_facts_cache 这个目录 ansible 会创建
//  fact_caching_timeout 在配置文件中每展示出来,表示 fact 缓存有效期,单位秒 
//  fact_caching_timeout 一般设置为1天(86400秒)
```



```javascript
// 执行一次，让其缓存 facts
[root@localhost ~]# ansible-playbook -i hosts checkhosts-two.yml --limit master
// 省略......

// 再执行一次, 发现速度明显快了很多
[root@localhost ~]# ansible-playbook -i hosts checkhosts-two.yml --limit master
// 省略......

// 查看缓存的文件
[root@localhost ~]# ls /dev/shm/ansible_facts_cache/
192.168.32.100
[root@localhost ~]# cat /dev/shm/ansible_facts_cache/192.168.32.100
// 缓存的 facts 信息

// 过了有效期再次执行, 然后又会重新获取 facts
[root@localhost ~]# ansible-playbook -i hosts checkhosts-two.yml --limit master
// 省略......


```

