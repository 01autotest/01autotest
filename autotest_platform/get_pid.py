#-*- encoding:UTF-8 -*-
import os
import sys
import string
#import psutil
import re
from subprocess import PIPE,Popen,check_output

def get_pid(var1):
    process_list = list(psutil.process_iter())
    process_list = map(str,process_list)
    tmp_pid = ''
    for rec in process_list:
        end = rec.find(".exe")
        name = rec[rec.find("'")+1:end] + '.exe'
        if(name == var1):    #不能用in，用==，防止重名
            tmp_pid = rec[15:]
    print(tmp_pid)
    end = tmp_pid.find(',')
    pid = tmp_pid[4:end]
    print(pid)
    return pid

def get_pids(var1):
    process_list = list(psutil.process_iter())
    process_list = map(str,process_list)
    tmp_pids = []
    for rec in process_list:
        end = rec.find(".exe")
        name = rec[rec.find("'")+1:end] + '.exe'
        if(name == var1):    #不能用in，用==，防止重名
            print(rec)
            tmp_pid = rec[15:]
            end = tmp_pid.find(',')
            pid = tmp_pid[4:end]
            tmp_pids.append(pid)
    print(tmp_pids)
    return tmp_pids

def get_adb_pid():
    pid = []
    ps = check_output(args='tasklist',shell=True)#阻塞性，管道中取出来
    # print ps.decode('gbk')
    li = ps.splitlines()  # 存入列表中
    # print li
    for one in li:
        if 'adb.exe' in one:
            print(one.split())
            tmp = re.split('\s',one)
            print(tmp)
            pid.append(one[30:34].strip())
    print('adb pid is: {}'.format(pid))
    return pid
