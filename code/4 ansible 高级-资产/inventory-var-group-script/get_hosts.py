#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
# argparse 模块可以处理参数
import argparse

def lists():
    """
    indent 定义输出时的格式缩进的空格数
    """
    dic = {}
    # range(99,100) 包含99,不包含100
    host_list = ['192.168.32.{}'.format(str(i)) for i in range(99,100)]
    host_dict = {'hosts': host_list}
    # 静态文件中的组,在这里定义了主机信息
    dic['computes'] = host_dict
    return json.dumps(dic, indent=4)

def hosts(name):
    dic = {'ansible_ssh_pass': 'admin000'}
    return json.dumps(dic)

# 指定脚本通用的语法,当这个文件被作为执行文件执行的时候,而不是作为模块导入的时候，—__name__ 的变量值就会等于 __main__
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # action='store'是固定写法
    parser.add_argument('-l', '--list', help='host list', action='store_true')
    parser.add_argument('-H', '--host', help='host vars')
    args = vars(parser.parse_args())

    if args['list']:
        print(lists())
    elif args['host']:
        print(hosts(args['host']))
    else:
        parser.print_help()