1. 使用 -i 指定自定义资产

资产可以不用 -i 指定，用 -i 指定肯定就是自定义资产。

如果不指定默认用 /etc/ansible/hosts, 但这个文件是可以更改。





2. 配置自定义资产为默认路径

```javascript
// 查看 ansible 配置文件
[root@localhost ~]# cat /etc/ansible/ansible.cfg 
# config file for ansible -- https://ansible.com/
# ===============================================

# nearly all parameters can be overridden in ansible-playbook
# or with command line flags. ansible will read ANSIBLE_CONFIG,
# ansible.cfg in the current working directory, .ansible.cfg in
# the home directory or /etc/ansible/ansible.cfg, whichever it
# finds first

[defaults]

# some basic default values...

#这里可以配置资产默认路径,这里虽然没有打开这个路径,但默认还是 /etc/ansible/hosts  
#inventory      = /etc/ansible/hosts
#library        = /usr/share/my_modules/
#module_utils   = /usr/share/my_module_utils/
#remote_tmp     = ~/.ansible/tmp
#local_tmp      = ~/.ansible/tmp
#plugin_filters_cfg = /etc/ansible/plugin_filters.yml

```





3. 自定义模块

自定义模块除非比较特殊的情况下，否则基本用不上，因为模块已经够丰富了，并且都把功能分类了。

```javascript
// -l 表示列出所有的模块
[root@localhost ~]# ansible-doc -l

// 目前已经有 3387 个模块
[root@localhost ~]# ansible-doc -l | wc -l
3387
```





4. 获取模块帮助文档

```javascript
[root@localhost ~]# ansible-doc -l | grep copy
vsphere_copy                                                  Copy a file to a VMware datastore                                                                                                             
win_copy                                                      Copies files to remote locations on windows hosts                                                                                             
bigip_file_copy                                               Manage files in datastores on a BIG-IP                                                                                                        
ec2_ami_copy                                                  copies AMI between AWS regions, return new image id                                                                                           
win_robocopy                                                  Synchronizes the contents of two directories using Robocopy                                                                                   
copy                                                          Copy files to remote locations                                                                                                                
na_ontap_lun_copy                                             NetApp ONTAP copy LUNs                                                                                                                        
icx_copy                                                      Transfer files from or to remote Ruckus ICX 7000 series switches                                                                              
unarchive                                                     Unpacks an archive after (optionally) copying it from the local machine                                                                       
ce_file_copy                                                  Copy a file to a remote cloudengine device over SCP on HUAWEI CloudEngine switches                                                            
postgresql_copy                                               Copy data between a file/program and a PostgreSQL table                                                                                       
ec2_snapshot_copy                                             copies an EC2 snapshot and returns the new Snapshot ID                                                                                        
nxos_file_copy                                                Copy a file to a remote NXOS device                                                                                                           
netapp_e_volume_copy                                          NetApp E-Series create volume copy pairs

// 获取 copy 模块帮助文档
[root@localhost ~]# ansible-doc copy
> COPY    (/usr/lib/python2.7/site-packages/ansible/modules/files/copy.py)

        The `copy' module copies a file from the local or remote machine to a location on the remote machine. Use the [fetch] module to copy files from remote
        locations to the local box. If you need variable interpolation in copied files, use the [template] module. Using a variable in the `content' field will result
        in unpredictable output. For Windows targets, use the [win_copy] module instead.

  * This module is maintained by The Ansible Core Team
  * note: This module has a corresponding action plugin.

OPTIONS (= is mandatory):

- attributes
        The attributes the resulting file or directory should have.
        To get supported flags look at the man page for `chattr' on the target system.
        This string should contain the attributes in the same order as the one displayed by `lsattr'.
        The `=' operator is assumed as default, otherwise `+' or `-' operators need to be included in the string.
        (Aliases: attr
// 省略......

// 查看 copy 模块简单的帮助信息
[root@localhost ~]# ansible-doc -s copy
- name: Copy files to remote locations
  copy:
      attributes:            # The attributes the resulting file or directory should have. To get supported flags look at the man page for `chattr' on the target system. This string should contain the
                               attributes in the same order as the one displayed by `lsattr'. The `=' operator is assumed as default, otherwise `+' or `-' operators need to be
                               included in the string.
      backup:                # Create a backup file including the timestamp information so you can get the original file back if you somehow clobbered it incorrectly.
      checksum:    
// 省略......   
                 
```

