# -*- coding: utf-8 -*-
import os
import xlrd

#==获取测试套列表
def get_test_scripts(var1):
    os.chdir('/')    #切换到相对路径
    # print os.getcwd()
    path = "static/test_scripts/"+var1+"/"
    tmp = os.listdir(path)
    test_scripts = []
    for rec in tmp:
        if rec.startswith('test_suit_'):
            # tmp1 = str(rec,'gbk')
            tmp1 = rec.encode("utf8")
            # tmp1 = tmp1.replace('test_suit_','')
            test_scripts.append(tmp1)
    return test_scripts

#==获取shell服务列表
def get_CI_shell():
    shells = []
    File = '/static/interface_excel/CI_shell.xlsx'
    data = xlrd.open_workbook(File)
    table = data.sheets()[0]
    rows = table.nrows
    cols = table.ncols
    for i in range(1,rows):
        var = []
        for j in range(0,cols):
            tmp = table.row_values(i)[j]
            tmp1 = "'%s'" %tmp
            var.append(tmp1)

        #===将读取的信息给赋值给变量===
        row_data = []
        for k in range(3):
            row_data.append(eval(var[k]))
        shells.append(row_data)
    return shells

#==获取接口列表
def get_interfaces():
    interfaces = []
    File = '/static/upload/interfaces.xlsx'
    data = xlrd.open_workbook(File)
    table = data.sheets()[0]
    rows = table.nrows
    cols = table.ncols
    for i in range(1,rows):
        var = []
        for j in range(0,cols):
            tmp = table.row_values(i)[j]
            if(j != 4):
                tmp1 = '"%s"' %tmp
            else:
                tmp1 = tmp
            var.append(tmp1)

        #===将读取的信息给赋值给变量===
        num = var[0]
        describe = eval(var[1])
        url = eval(var[2])
        if(var[3] != '""'):
            head = eval(eval(var[3]))
        else:
            head = ''
        # body = eval(eval(var[4]))
        body = eval(var[4])
        mode = eval(var[5])
        interfaces.append((num,describe,url,head,body,mode))
    return interfaces

#==获取分享列表
def get_shares():
    shares = []
    File = '/static/interface_excel/shares.xlsx'
    data = xlrd.open_workbook(File)
    table = data.sheets()[0]
    rows = table.nrows
    cols = table.ncols
    for i in range(1,rows):
        var = []
        for j in range(0,cols):
            tmp = table.row_values(i)[j]
            tmp1 = "'%s'" %tmp
            var.append(tmp1)

        #===将读取的信息给赋值给变量===
        row_data = []
        for k in range(9):
            row_data.append(eval(var[k]))
        shares.append(row_data)
    return shares


# #==将测试套移动到view_test_scripts目录，并更改编码
# def move_test_suit():
#     test_scripts = get_test_scripts()
#     for rec in test_scripts:
#         #==迁移
#         tmp = unicode(rec,'utf8')
#         tmp = tmp.encode("gbk")
#         File1='/autotest_platform/autotest_platform/static/test_scripts/'+tmp+'/main.py'
#         File2='/autotest_platform/autotest_platform/static/test_scripts/'+tmp+'/main1.py'
#         shutil.copy(File1,File2)
#         print tmp,'/main1.py   copy   success!'
#
#         #==更改编码
#         File = open(File2,'r+')
#         result = File.read()
#         open(File2,'w').write(re.sub(r'coding: utf-8', r'coding: gb2312', result))
#         File.close()
#
#         print tmp,'/main1.py   coding   succes!'
#
# move_test_suit()