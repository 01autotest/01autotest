# -*- coding: utf-8 -*-
import time,traceback
import json,requests
#from methods import *
from celery import Celery
from apps.app_interface.celery import app
from idlelib.rpc import response_queue
session = requests.Session()
import requests, time, sys, re
import urllib, zlib
from djcelery.schedulers import DatabaseScheduler

#==基础函数
def request_post(url,body,head,body_format):
    if(body_format == '1'):
        body = json.dumps(body)
    else:
        keys = body.keys()
        for rec in keys:
            if('[{' in str(body[rec]) and '}]' in str(body[rec])):
                body = json.dumps(body)
                print(u'body已进行json格式转换！')
                break
    r = session.post(url,body,headers = head)
    return r

def request_upload_pic(url,data,head):
    files = {'roomFile': ("test.jpg",open("/static/upload/test.jpg", 'rb'),'image/jpeg')}
    r = session.post(url, data=data, files=files, headers=head)
    return r

def request_get(url,body,head,body_format):
    if(body_format == '1'):
        body = json.dumps(body)
    r = session.get(url,params = body, headers=head)
    return r

def Method_POST(url,body,head, body_format,is_out = True):
    r = request_post(url, body, head, body_format)
    if(is_out == True):
     #   print_log('【响应状态码】：', ','),print_log(str(r.status_code), ','), print_log(str(r.reason))
     #   print_log('【接口url】：', ','), print_log(r.url)
     #   print_log('【请求参数】：',), print_log(body)
        print(body)
    # resp
    response = r.text
    # cookie
    cookie = '; '.join(['='.join(rec) for rec in session.cookies.items()])
    if(is_out == True):
     #   print_log('【接口输出】：'), print_log(str(response))
        print(response)
    return response,cookie

def Method_UPLOAD_PIC(url, body, head,is_out = True):
    r = request_upload_pic(url, body, head)
    if(is_out == True):
     #   print_log('【响应状态码】：', ','),print_log(str(r.status_code), ','), print_log(str(r.reason))
     #   print_log('【接口url】：', ','), print_log(r.url)
        print('【请求参数】：',), print(body)
    # resp
    response = r.text
    # cookie
    cookie = '; '.join(['='.join(rec) for rec in session.cookies.items()])
    if(is_out == True):
        print('【接口输出】：'), print(str(response))
    return response,cookie

def Method_GET(url, body, head, body_format,is_out = True):
    r = request_get(url, body, head, body_format)
    if(is_out == True):
     #   print_log('【响应状态码】：', ','),print_log(str(r.status_code), ','), print_log(str(r.reason))
     #   print_log('【接口url】：', ','), print_log(r.url)
        print('【请求参数】：',), print(body)
    # resp
    response = r.text
    if(is_out == True):
        generate_result(response)
    # cookie
    cookie = '; '.join(['='.join(rec) for rec in session.cookies.items()])
    if(is_out == True):
        print('【接口输出】：'),print(response)
    return response,cookie

#==测试开始，去掉多线程之后，递归执行是光速！！！
def interface_test_start(url,body,head,mode,body_format,is_out):
    try:
        if(mode == 'POST' or mode == 'post'):
            response,cookie = Method_POST(url,body,head,body_format,is_out)
        elif(mode == 'upload_pic' or mode == 'UPLOAD_PIC'):
            response,cookie = Method_UPLOAD_PIC(url,body,head,is_out)
        elif(mode == 'GET' or mode == 'get'):
            response,cookie = Method_GET(url,body,head,body_format,is_out)

     #   print_log('')

        return response,cookie

    except Exception:
        error_info = traceback.format_exc()
      #  print_log(error_info)
        return 1

#==断言
def assert_is_success(result,assert_keywords,is_contain,is_out = True):
    if(is_contain == '1'):
        if(assert_keywords in result):
            if(is_out == True):
                print('\n【测试结果】： 测试通过')
            else:
                print('测试结果： 测试通过')
            return 0
        else:
            if(is_out == True):
                print('\n【测试结果】： 测试失败，断言不匹配')
            else:
                print('测试结果： 测试失败，断言不匹配')
            return 1
    elif(is_contain == '0'):
        if(assert_keywords not in result):
            if(is_out == True):
                print('\n【测试结果】： 测试通过')
            else:
                print('测试结果： 测试通过')
            return 0
        else:
            if(is_out == True):
                print('\n【测试结果】： 测试失败，断言不匹配')
            else:
                print('测试结果： 测试失败，断言不匹配')
            return 1

def assert_test(assert_url,assert_head,assert_mode,assert_body,assert_keywords,is_contain,assert_body_format,is_out):
    try:
        assert_keywords = assert_keywords.replace(' ','').replace('\n','').replace('\t','').replace('\r','')
        print('assert_keywords = ',assert_keywords,'\n')
        if (assert_mode == 'POST' or assert_mode == 'post'):
            print(assert_url,assert_body,assert_head)
            r = request_post(assert_url,assert_body,assert_head,assert_body_format)
            result = r.text.replace(' ','').replace('\n','').replace('\t','').replace('\r','')
            assert_result = assert_is_success(result,assert_keywords,is_contain,is_out)
        elif (assert_mode == 'upload_pic' or assert_mode == 'UPLOAD_PIC'):
            r = request_upload_pic(assert_url,assert_body,assert_head)
            result = r.text.replace(' ','').replace('\n','').replace('\t','').replace('\r','')
            assert_result = assert_is_success(result,assert_keywords,is_contain,is_out)
        elif (assert_mode == 'GET' or assert_mode == 'get'):
            r = request_get(assert_url,assert_body,assert_head,assert_body_format)
            result = r.text.replace(' ','').replace('\n','').replace('\t','').replace('\r','')
            assert_result = assert_is_success(result,assert_keywords,is_contain,is_out)

       # print_log('')
        return assert_result

    except Exception:
        error_info = traceback.format_exc()
      #  print_log(error_info)
        return 2

def assert_test_old(response,assert_keywords_old,is_out):
    try:
        assert_keywords = assert_keywords_old.replace(' ','').replace('\n','').replace('\t','').replace('\r','')
        result = response.replace(' ','').replace('\n','').replace('\t','').replace('\r','')
        print('assert_keywords = ',assert_keywords,'\n')
        assert_result = assert_is_success(result,assert_keywords,'1',is_out)

     #   print_log('')
        return assert_result

    except Exception:
        error_info = traceback.format_exc()
     #   print_log(error_info)
        return 2

@app.task
def hello_world():
    print('已运行')

@app.task
def start_interface_suit1(request):
    if request.method == "POST":
        try:
            raw_data = request.body
            raw_data = json.loads(raw_data)
            cur_id = raw_data['cur_id']

            #==公共参数 - keyword
            public_list = public_para1.objects.filter(~Q(keywords__icontains='AI'))
            keyword_list = ["{"+rec.keywords+"}" for rec in public_list]

            #==公共参数 - dict - 公共参数
            public_list1 = public_para1.objects.filter(Q(module='pub'),~Q(keywords__icontains='AI'))
            keyword_list1 = ["{"+rec.keywords+"}" for rec in public_list1]
            public_dict1 = {}
            for rec in public_list1:
                public_dict1[rec.keywords] = rec.value

            #==公共参数 - dict - 接口返回值
            public_list2 = public_para1.objects.filter(module='suit').filter(~Q(keywords__icontains='AI'))
            keyword_list2 = ["{"+rec.keywords+"}" for rec in public_list2]
            public_dict2 = {}
            for rec in public_list2:
                public_dict2[rec.keywords] = str((rec.left,rec.right,rec.index))

            #==公共参数 - dict - all
            public_dict = {}
            public_dict.update(public_dict1)
            public_dict.update(public_dict2)

            #==清空日志文件
            f_handler = open('/autotest_platform/test_out.log', 'w')
            f_handler.truncate()
            f_handler.close()

         #   print_log('cur_id: ',','),print_log(cur_id)
            cur_interface = suit_interface.objects.filter(id=cur_id)[0]

            # 映射url
            url = cur_interface.url
            if("{" in url and "}" in url):
                end_index = url.find("}")
                key_url = url[:end_index+1]
                url = url.replace(key_url,public_dict[key_url.replace('{','').replace('}','')])

            # 映射head
            head = eval(cur_interface.head)
            for rec in head.keys():
                if(head[rec] in keyword_list1):
                    head[rec] = public_dict[head[rec].replace('{','').replace('}','')]
                elif(head[rec] in keyword_list2):
                    try:
                        head[rec] = cache.get(head[rec].replace('{','').replace('}',''))
                    except Exception:
                        return HttpResponse('【ERROR】：参数 '+head[rec]+' 没有参数值，请确认是否已执行返回 '+head[rec]+' 的接口')
            print(head)

            # 映射body
            body = eval(cur_interface.body)
            for rec in body.keys():
                if(isinstance(body[rec],str)):  #参数为整数或者小数不需要映射
                    # 替换关键字
                    for rec1 in keyword_list1:
                        if(rec1 in body[rec]):
                            body[rec] = body[rec].replace(rec1, public_dict[rec1.replace('{','').replace('}','')])
                    for rec2 in keyword_list2:
                        if(rec2 in body[rec]):
                            try:
                                body[rec] = body[rec].replace(rec2, cache.get(rec2.replace('{','').replace('}','')))
                            except Exception:
                                return HttpResponse('【ERROR】：参数 '+rec2+' 没有参数值，请确认是否已执行返回 '+rec2+' 的接口')
                    # 替换sql
                    if('select' in body[rec]):
                        sql = body[rec]
                        cursor = connection.cursor()
                        print(sql)
                        cursor.execute(sql)
                        data = cursor.fetchall()
                        print(u'查询的结果为： ',data[0][0])
                        body[rec] = data[0][0]
            print(body)

            mode = cur_interface.mode
            body_format = cur_interface.body_format

            #==测试开始
            response,cookie = interface_test_start(url,body,head,mode,body_format,True)     #False，不打印日志；True，打印日志

            # 更新cookie
            update_cookie = cur_interface.update_cookie
            if('{' in update_cookie and '}' in update_cookie):
                for rec in keyword_list1:
                    if(rec == update_cookie):
                        cookie_status1 = public_para1.objects.filter(keywords=rec.replace('{','').replace('}','')).update(value=cookie)
                        print(cookie_status1, ' update success!')
                        break

            # 返回值存入缓存，保留30秒
            public_resp = public_para1.objects.filter(module_id=int(cur_id),module='suit')
            if(str(public_resp) != '[]'):
                for rec in public_resp:
                    left = rec.left
                    right = rec.right
                    index = int(rec.index)
                    reg = left+'.+?'+right
                    result_all = re.findall(reg,response)
                    try:
                        result_tmp = result_all[index]
                        start = len(left)
                        end = len(result_tmp) - len(right)
                        result = result_tmp[start:end]
                        print(rec.keywords,'匹配结果为：',result)
                        # 写入缓存
                        cache.set(rec.keywords, result, timeout=300)
                    except Exception:
                        print((rec.keywords,left,right,index),' 在返回结果中未匹配到')

            # 断言
            is_new = cur_interface.assert_use_new
            if(is_new == '1'):
                assert_url = cur_interface.assert_url
                assert_head = eval(cur_interface.assert_head)
                # 映射assert_head
                for rec in assert_head.keys():
                    if(assert_head[rec] in keyword_list1):
                        assert_head[rec] = public_dict[assert_head[rec].replace('{','').replace('}','')]
                    elif(assert_head[rec] in keyword_list2):
                        try:
                            assert_head[rec] = cache.get(assert_head[rec].replace('{','').replace('}',''))
                        except Exception:
                            return HttpResponse('【ERROR】：参数 '+assert_head[rec]+' 没有参数值，请确认是否已执行返回 '+assert_head[rec]+' 的接口')
                print(assert_head)
                # assert_mode
                assert_mode = cur_interface.assert_mode
                assert_body = eval(cur_interface.assert_body)
                # 映射assert_body
                for rec in assert_body.keys():
                    if(isinstance(assert_body[rec],str)):  #参数为整数或者小数不需要映射
                        # 替换关键字
                        for rec1 in keyword_list1:
                            if(rec1 in assert_body[rec]):
                                assert_body[rec] = assert_body[rec].replace(rec1, public_dict[rec1.replace('{','').replace('}','')])
                        for rec2 in keyword_list2:
                            if(rec2 in assert_body[rec]):
                                try:
                                    assert_body[rec] = assert_body[rec].replace(rec2, cache.get(rec2.replace('{','').replace('}','')))
                                except Exception:
                                    return HttpResponse('【ERROR】：参数 '+rec2+' 没有参数值，请确认是否已执行返回 '+rec2+' 的接口')
                        # 替换sql
                        if('select' in assert_body[rec]):
                            sql = assert_body[rec]
                            cursor = connection.cursor()
                            print(sql)
                            cursor.execute(sql)
                            data = cursor.fetchall()
                            print(u'查询的结果为： ',data[0][0])
                            assert_body[rec] = data[0][0]
                print(assert_body)
                # assert_keywords
                assert_keywords = cur_interface.assert_keywords
                # 映射assert_keywords
                for rec1 in keyword_list1:
                    if(rec1 in assert_keywords):
                        assert_keywords = assert_keywords.replace(rec1, public_dict[rec1.replace('{','').replace('}','')])
                for rec2 in keyword_list2:
                    if(rec2 in assert_keywords):
                        try:
                            assert_keywords = assert_keywords.replace(rec2, cache.get(rec2.replace('{','').replace('}','')))
                        except Exception:
                            return HttpResponse('【ERROR】：参数 '+rec2+' 没有参数值，请确认是否已执行返回 '+rec2+' 的接口')
                # 替换sql
                if('select' in assert_keywords):
                    sql = assert_keywords
                    cursor = connection.cursor()
                    print(sql)
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    print(u'查询的结果为： ',data[0][0])
                    assert_keywords = data[0][0]
                # is_contain
                is_contain = cur_interface.assert_keywords_is_contain
                # assert_body_format
                assert_body_format = cur_interface.assert_body_format
                tt=assert_test(assert_url,assert_head,assert_mode,assert_body,assert_keywords,is_contain,assert_body_format,True)
                if tt:
                    api_test_result(cur_id, response, 1)
                    print('testresult=测试通过')
                else:
                    api_test_result(cur_id, response, 0)
                    print('testresult=测试不通过')
                time.sleep(0.1)
            else:
                # assert_keywords_old
                assert_keywords_old = cur_interface.assert_keywords_old
                # 替换关键字
                for rec1 in keyword_list1:
                    if(rec1 in assert_keywords_old):
                        assert_keywords_old = assert_keywords_old.replace(rec1, public_dict[rec1.replace('{','').replace('}','')])
                for rec2 in keyword_list2:
                    if(rec2 in assert_keywords_old):
                        try:
                            assert_keywords_old = assert_keywords_old.replace(rec2, cache.get(rec2.replace('{','').replace('}','')))
                        except Exception:
                            return HttpResponse('【ERROR】：参数 '+rec2+' 没有参数值，请确认是否已执行返回 '+rec2+' 的接口')
                # 替换sql
                if('select' in assert_keywords_old):
                    sql = assert_keywords_old
                    cursor = connection.cursor()
                    print(sql)
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    print(u'查询的结果为： ',data[0][0])
                    assert_keywords_old = data[0][0]
                # assert start
                tt=assert_test_old(response,assert_keywords_old,True)
                if tt:
                    api_test_result(cur_id, response, 1)
                    print('testresult=测试通过')
                else:
                    api_test_result(cur_id, response, 0)
                    print('testresult=测试不通过')

            #==日志
            File = '/autotest_platform/test_out.log'
            File1 = open(File,'r',encoding='utf-8')
            test_log = File1.readlines()
            #==去掉test_log中的'<>'，否则textarea中无法看到输入结果
            test_log = str(test_log)
            test_log = test_log.replace('<','[').replace('>',"]")
            test_log = eval(test_log)
            return HttpResponse(test_log)
        except Exception:
            error_info = traceback.format_exc()
            return HttpResponse(error_info)
