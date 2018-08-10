# -*- coding: utf-8 -*-
from __future__ import absolute_import
# from celery import task
# from celery import shared_task
import os
#import paramiko
#from apps.app_performance.models import *
#import psutil
import subprocess
import time,datetime,threading
from config import *
from get_pid import *
from django.db import connection

#==获取性能参数写入日志
# @shared_task()
def get_performances_into_logs(var1,var2):
    linux_ip = linux_ip1
    linux_user = linux_user1
    linux_password = linux_passwd1

    #==连接Linux
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(linux_ip, 22, linux_user, linux_password)

    File = '/static/logs/'+var2
    File1 = open(File,'a')
    stdin, stdout, stderr = ssh.exec_command(var1)
    out = stdout.readlines()
    out = [rec.replace('\n','') for rec in out]
    for rec in out:
        if(rec != ''):
            print(rec)
            File1.write(rec+'\n')
    File1.close()
    print()

#==获取性能参数
def get_performances(var1):
    linux_ip = '192.168.0.96'
    linux_user = 'liqing'
    linux_password = 'liqing20170621'

    #==连接Linux
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(linux_ip, 22, linux_user, linux_password)

    stdin, stdout, stderr = ssh.exec_command(var1)
    out = stdout.readlines()
    out = [rec.replace('\n','') for rec in out]
    tmp = out[0].split(' ')
    return tmp

#==获取性能参数插入数据库
# @shared_task()
def insert_sql_performances():
    now = datetime.datetime.now()
    present_time = now.strftime("%Y-%m-%d %H:%M:%S")

    #==cpu
    cpu_info = get_performances("sar -P ALL 1 1|grep Average|grep -v CPU|head -1|awk '{print $3,$5,$6,$8}'")
    cpu_info = cpu(user=cpu_info[0],system=cpu_info[1],iowait=cpu_info[2],idle=cpu_info[3],date_time=present_time)
    cpu_info.save()

    #==内存
    mem_info = get_performances("sar -r 1 1|grep Average|awk '{print $2,$3,$4}'")
    mem_info = mem(free=mem_info[0],used=mem_info[1],used_pct=mem_info[2],date_time=present_time)
    mem_info.save()

    #=磁盘
    disk_info = get_performances("sar -dp 1 1|grep Average|grep sda|awk '{print $3,$4,$5}'")
    disk_info = disk(tps=disk_info[0],rd_sec=disk_info[1],wr_sec=disk_info[2],date_time=present_time)
    disk_info.save()

    #==lo
    lo_info = get_performances("sar -n DEV 1 1|grep Average|grep -v IFACE|grep lo|awk '{print $3,$4}'")
    lo_info = flow_lo(rxpck=lo_info[0],txpck=lo_info[1],date_time=present_time)
    lo_info.save()

    # #==em
    # em_info = get_performances("sar -n DEV 1 1|grep Average|grep -v IFACE|grep lo|awk '{print $3,$4}'")
    # em_info = flow_em(rxpck=em_info[0],txpck=em_info[1],date_time=present_time)
    # em_info.save()

    #==eth0
    eth0_info = get_performances("sar -n DEV 1 1|grep Average|grep -v IFACE|grep eth0|awk '{print $3,$4}'")
    eth0_info = flow_eth0(rxpck=eth0_info[0],txpck=eth0_info[1],date_time=present_time)
    eth0_info.save()

    # #==eth1
    # eth1_info = get_performances("sar -n DEV 1 1|grep Average|grep -v IFACE|grep eth0|awk '{print $3,$4}'")
    # eth1_info = flow_eth1(rxpck=eth1_info[0],txpck=eth1_info[1],date_time=present_time)
    # eth1_info.save()
    #
    # #==eth2
    # eth2_info = get_performances("sar -n DEV 1 1|grep Average|grep -v IFACE|grep eth0|awk '{print $3,$4}'")
    # eth2_info = flow_eth2(rxpck=eth2_info[0],txpck=eth2_info[1],date_time=present_time)
    # eth2_info.save()

    print('success insert!')

#==获取当前数据库性能
def get_sql_performances():
    cursor = connection.cursor()
    cursor.execute('show global status like "Question%";')
    QPS = cursor.fetchall()

    cursor.execute('show global status like "Com_commit";')
    Com_commit = cursor.fetchall()

    cursor.execute('show global status like "Com_rollback";')
    Com_rollback = cursor.fetchall()

    Com = str(int(Com_commit) + int(Com_rollback))

    cursor.execute('show global status like "Threads_connected";')
    connected = cursor.fetchall()

    return [QPS,Com,connected]

#==获取当前服务器性能
def get_server_performances():
    cpu_info = cpu.objects.order_by('-id').all()[0]     #order by,limit     [1:3]
    mem_info = mem.objects.order_by('-id').all()[0]
    disk_info = disk.objects.order_by('-id').all()[0]
    lo_info = flow_lo.objects.order_by('-id').all()[0]
    eth0_info = flow_eth0.objects.order_by('-id').all()[0]

    return cpu_info,mem_info,disk_info,lo_info,eth0_info

#==检测进程并自动拉起
# @shared_task()
def start_service():
    process_list = list(psutil.process_iter())
    process_list = map(str,process_list)
    cmd_sum = 0
    for rec in process_list:
        if('cmd' in rec):
            cmd_sum += 1
    if(cmd_sum != 3):
        os.chdir('/autotest_platform')
        os.system('python manage.py runserver 192.168.6.162:1013')

#===================================app流量测试===================================
def get_uid_and_packages():
    uids = []
    uid = ''
    packages = []
    package = ''
    cmd = 'adb shell dumpsys package packages | findstr /c:"userId" /c:"Package ["'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = proc.communicate()[0]
    output = output.decode()
    for line in output.split('\n'):
        # 判断结果里面是否有userId
        if 'userId=' in line:
            # 找到 userId= 的下标
            index = line.find('userId=')
            # 从 userId= 的下标+7，开始遍历，直到字符串结束
            for i in range((index + 7), len(line)):
                # 如果是数字，就拼接到uid
                if line[i].isdigit():
                    uid = uid + line[i]
                else:
                    # 不是数字的时候，就停止拼接，初始化uid
                    uids.append(uid)
                    uid = ''
                    break
        # 判断结果里面是否有Package [
        elif 'Package [' in line:
            # 找到 Package [ 的下标
            index_start = line.find('[')
            index_end = line.find(']')
            # 从"["到"]"这里面的是package
            package = line[index_start + 1:index_end]
            packages.append(package)
    return [uids, packages]

def remove_duplicate_pid():
    '''
    去掉重复的pid，获得整个设备的uid，package
    :return:
    '''
    uids=get_uid_and_packages()[0]
    packages=get_uid_and_packages()[1]
    uid_and_packages=[]
    for i in range(len(packages)):
        #单个uid和package
        uid_package=[]
        #判定是否有重复的uid的标志位
        flag=0
        uid_package.append(uids[i])
        uid_package.append(packages[i])
        for up in uid_and_packages:
            #如果要加入的pid与已经存在相同，标志位置为1
            if up[0] == uids[i]:
                flag=1
        #如果有重复的就去掉重复的，不添加
        if flag==0:
            uid_and_packages.append(uid_package)
    return uid_and_packages

def get_per_flow(uid):
    '''
    根据uid获取流量
    :param uid:
    :return:
    '''
    # 获取流量的adb命令
    cmd = 'adb shell cat /proc/net/xt_qtaguid/stats | find "' + uid + '"'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = proc.communicate()[0].decode().split('\n')
    # 数据流量
    rmnet = 0
    # wifi流量
    wlan = 0
    for line in output:
        # 第6列数据是下行/接收流量，第八列数据是上行/发送流量
        if 'rmnet' in line:
            rmnet = rmnet + int(line.split(' ')[5]) + int(line.split(' ')[7])
        elif 'wlan' in line:
            wlan = wlan + int(line.split(' ')[5]) + int(line.split(' ')[7])
    return rmnet, wlan

def get_flows():
    '''
    获取所有的包名和对应流量
    :return:返回数据为 [[包名1,数据流量1,wifi流量1],[包名2,数据流量2,wifi流量2],[包名3,数据流量3,wifi流量3]...]
    '''
    package_flows = []
    for uid_package in remove_duplicate_pid():
        rmnet = 0
        wlan = 0
        package_flow = []
        # 根据每一个uid查到对应的数据流量和wifi流量
        rmnet, wlan = get_per_flow(uid_package[0])
        # 如果数据流量和wifi流量都为0，就不统计
        if rmnet == 0 and wlan == 0:
            pass
        else:
            # print(uid_package[1]+':\n'+'data:'+str(rmnet)+',wifi:'+str(wlan)+'\n')
            # 添加包
            package_flow.append(uid_package[1])
            # 添加数据流量
            rmnet = float(rmnet) / 1024 / 1024
            rmnet = float('%.3f' % (rmnet))
            package_flow.append(rmnet)
            # 添加wifi流量
            wlan = float(wlan) / 1024 / 1024
            wlan = float('%.3f' % (wlan))
            package_flow.append(wlan)
            # 把这个app的包名,数据流量,wifi流量加入到list里面
            package_flows.append(package_flow)
    print(package_flows)
    print(len(package_flows))
    return package_flows

#===================================流量耗用实时统计===================================

def get_uid_apk(package):
    '''
    获取uid
    :param package:
    :return:
    '''
    uid = ''
    # 获取uid
    cmd = 'adb shell dumpsys package ' + package + ' | find "userId"'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # 保留返回结果第一行
    output = proc.communicate()[0].decode().split('\n')[0]
    # 去掉空格
    output = output.replace(' ', '')
    # 判断结果里面是否有userId
    if 'userId=' in output:
        # 找到 userId= 的下标
        index = output.find('userId=')
        # 从 userId= 的下标+7，开始遍历，直到字符串结束
        for j in range((index + 7), len(output)):
            # 如果是数字，就拼接到uid
            if output[j].isdigit():
                uid = uid + output[j]
            else:
                # 不是数字的时候，就停止拼接
                break
        return uid
    else:
        print('Not found uid')
        return '0'

def get_flow_apk(package='com.oecommunity.oeshop'):
    '''
    根据uid获取流量
    :param package:
    :return:
    '''
    uid = get_uid_apk(package)
    # 获取当前时间
    # ltime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    # 获取流量的adb命令
    cmd = 'adb shell cat /proc/net/xt_qtaguid/stats | find "' + uid + '"'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = proc.communicate()[0].decode().split('\n')
    # 数据流量
    rmnet = 0
    # wifi流量
    wlan = 0
    # 总流量
    flow = 0
    for line in output:
        # 第6列数据是下行/接收流量，第八列数据是上行/发送流量
        if 'rmnet' in line:
            rmnet = rmnet + int(line.split(' ')[5]) + int(line.split(' ')[7])
        elif 'wlan' in line:
            wlan = wlan + int(line.split(' ')[5]) + int(line.split(' ')[7])
    flow = wlan + rmnet
    return flow
