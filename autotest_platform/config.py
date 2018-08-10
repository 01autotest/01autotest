# -*- coding: utf-8 -*-
import re

def get_config(name,type = 0):
    config = re.search('((?<!#)'+name+' = )(.+)',result).group(2)
    if(type == 1):
        config = int(config)
    return config

#=========================================配置信息=========================================
File = 'config.ini'
File1 = open(File,'r',encoding='UTF-8')
result = File1.read()

sql_host1 = get_config('sql_host1').replace('\r','')
sql_user1 = get_config('sql_user1').replace('\r','')
sql_passwd1 = get_config('sql_passwd1').replace('\r','')
sql_db1 = get_config('sql_db1').replace('\r','')
redis_ip1 = get_config('redis_ip1').replace('\r','')
linux_ip1 = get_config('linux_ip1').replace('\r','')
linux_user1 = get_config('linux_user1').replace('\r','')
linux_passwd1 = get_config('linux_passwd1').replace('\r','')