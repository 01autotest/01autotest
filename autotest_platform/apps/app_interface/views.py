# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from apps.app_interface.models import *
from django.db import connection
from apps.app_interface.tasks import *
from methods import *
import json, traceback, re, random
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.db.models import Avg, Max, Min, Sum, Count
from django.core.cache import cache
from django.template.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from djcelery.models import PeriodicTask, CrontabSchedule, IntervalSchedule
from .tasks import hello_world
from .tasks import start_interface_suit1
from djcelery.schedulers import DatabaseScheduler
from djcelery import loaders
import yagmail
#=============================================================== 公共参数 ===============================================================

#==公共参数列表
@login_required()
def show_public_para(request):
    para_list = public_para1.objects.filter(module='pub')    #只查公共参数，不查接口返回值
    cur_user = request.user.username
    # csrf
    c = csrf(request)
    c.update({'para_list': para_list,'cur_user': cur_user})
    return render_to_response("public_para.html",c)

#==添加公共参数
def add_public_para(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        name1 = raw_data['name1']
        keywords1 = raw_data['keywords1']
        value1 = raw_data['value1']

        #==insert public_info
        public_info = public_para1(name=name1,keywords=keywords1,value=value1,left='',right='',index='',module='pub',module_id='',type='公共参数')
        public_info.save()
        print(public_info,' insert success!')

        return HttpResponse('update public_para success!')

#==删除公共参数
def del_public_para(req):
    if req.method == "POST":
        raw_data = req.body
        raw_data = json.loads(raw_data)
        id1 = raw_data['id1']

        # del
        print(id1)
        public_para1.objects.filter(id=id1).delete()
        print('id = ',id1,' delete success!')
        return HttpResponse('delete success!')

#==保存修改公共参数
def save_public_para(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        public_para_list = raw_data['public_para_list']
        print(public_para_list)
        #==update
        for i in range(len(public_para_list)):
            status = public_para1.objects.filter(id=public_para_list[i][0]).update(name=public_para_list[i][1],value=public_para_list[i][2],keywords=public_para_list[i][3])
            print(status,' update success!')

        return HttpResponse('update status success!')

#==格式化body
def format_body(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        original_body = raw_data['original_body']
        print(original_body)

        fomated_body = {}

        #==把<>转换成[]，因为如果是html元素，页面会转义从而显示不出来
        if('<' in original_body or '>' in original_body):
            original_body = original_body.replace('<','[').replace('>',']')

        try:
            #==情况1，dict格式无需转换，因此不需要单独写含有:和=同时存在的情况（即XSS的情况），因为dict不进行任何处理
            if('{' in original_body and '}' in original_body):
                fomated_body = eval(original_body)
            #==情况2，key=value形式，仅一个参数
            elif('=' in original_body and '&' not in original_body):
                original_body = original_body.split('=')
                fomated_body[original_body[0]] = original_body[1]
            #==情况3，key=value&形式，多个参数
            elif('=' in original_body and '&' in original_body):
                original_body = original_body.strip('&').replace('&&','&')    #去除首尾&，并把&&替换成&
                #==判断&key=value的情况，只出现1个&
                equal_num = original_body.count('=')
                if(equal_num > 1):
                    original_body = original_body.split('&')
                    print(original_body)
                    tmp_key_list = []
                    for rec in original_body:
                        tmp = rec.split('=')
                        tmp = [rec1.replace(' ','') for rec1 in tmp]    #去掉多余空格
                        #==为fomated_body赋值，并处理多个相同key的情况
                        key = tmp[0].replace('"','').replace("'",'')    #去掉'或"，避免输出的内容有\"
                        value = tmp[1].strip(',').replace('"','').replace("'",'')  #去掉'或"，避免输出的内容有\"
                        if key in fomated_body:
                            #必须每次处理key都转换成list，而不能最后一起转
                            if (isinstance(fomated_body[key], list)):
                                tmp_key_str = ','.join(fomated_body[key])
                            else:
                                tmp_key_str = fomated_body[key]
                            key_str = str(tmp_key_str) + ',' + value
                            fomated_body[key] = key_str.split(',')
                            # fomated_body[key] = fomated_body[key] + ',' + value
                        else:
                            fomated_body[key] = value
                else:
                    original_body = original_body.split('=')
                    fomated_body[original_body[0]] = original_body[1]
            else:
                original_body = original_body.split('\n')
                print(len(original_body),original_body)
                if(':' in original_body):
                    #==情况4，冒号单独占一行
                    colon_num = original_body.count(':')
                    if(colon_num >= 1):
                        original_body = [rec.replace(' ','') for rec in original_body]  #去掉多余空格
                        #==为fomated_body赋值，并处理多个相同key的情况
                        tmp_key_list = []
                        for i in range(0,len(original_body),3):
                            key = original_body[i].replace('"','').replace("'",'')    #去掉'或"，避免输出的内容有\"
                            value = original_body[i+2].strip(',').replace('"','').replace("'",'')  #去掉'或"，避免输出的内容有\"
                            if key in fomated_body:
                                #必须每次处理key都转换成list，而不能最后一起转
                                if(isinstance(fomated_body[key],list)):
                                    tmp_key_str = ','.join(fomated_body[key])
                                else:
                                    tmp_key_str = fomated_body[key]
                                key_str = str(tmp_key_str) + ',' + value
                                fomated_body[key] = key_str.split(',')
                                # fomated_body[key] = fomated_body[key] + ',' + value
                            else:
                                fomated_body[key] = value
                    else:
                        #==情况5，key、value通过:分隔
                        for rec in original_body:
                            tmp = rec.split(':')
                            tmp = [rec1.replace(' ','') for rec1 in tmp]    #去掉多余空格
                            #==为fomated_body赋值，并处理多个相同key的情况
                            key = tmp[0].replace('"','').replace("'",'')    #去掉'或"，避免输出的内容有\"
                            value = tmp[1].strip(',').replace('"','').replace("'",'')  #去掉'或"，避免输出的内容有\"
                            if key in fomated_body:
                                #必须每次处理key都转换成list，而不能最后一起转
                                if(isinstance(fomated_body[key],list)):
                                    tmp_key_str = ','.join(fomated_body[key])
                                else:
                                    tmp_key_str = fomated_body[key]
                                key_str = str(tmp_key_str) + ',' + value
                                fomated_body[key] = key_str.split(',')
                                # fomated_body[key] = fomated_body[key] + ',' + value
                            else:
                                fomated_body[key] = value
                else:
                    #==情况6，key、value通过' '、\t、\r分隔
                    print()
                    tmp_key_list = []
                    for rec in original_body:
                        print(rec,'!!!!!!!!!!!')
                        if(':' in rec):
                            tmp = rec.split(':')
                        elif('\t' in rec):
                            tmp = rec.split('\t')
                        elif('\r' in rec):
                            tmp = rec.split('\r')
                        elif(' ' in rec):
                            tmp = rec.split(' ')
                        else:
                            tmp = rec.split('   ')
                        tmp = [rec1.replace(' ', '') for rec1 in tmp]   #去掉多余空格
                        ##==为fomated_body赋值，并处理多个相同key的情况
                        key = tmp[0].replace('"','').replace("'",'')    #去掉'或"，避免输出的内容有\"
                        value = tmp[1].strip(',').replace('"','').replace("'",'')  #去掉'或"，避免输出的内容有\"
                        if key in fomated_body:
                            #必须每次处理key都转换成list，而不能最后一起转
                            if(isinstance(fomated_body[key],list)):
                                tmp_key_str = ','.join(fomated_body[key])
                            else:
                                tmp_key_str = fomated_body[key]
                            key_str = str(tmp_key_str) + ',' + value
                            fomated_body[key] = key_str.split(',')
                            # fomated_body[key] = fomated_body[key] + ',' + value
                        else:
                            fomated_body[key] = value

            print(fomated_body)

            #==格式化fomated_body
            fomated_body1 = json.dumps(fomated_body,sort_keys=True,indent=8)
            # print fomated_body1.decode('raw_unicode_escape')

            fomated_body_list = {"json_str": fomated_body1.encode().decode('raw_unicode_escape'),    #显示中文，只适用于json
                                 "json_dict":json.dumps(fomated_body,sort_keys=True).encode().decode('raw_unicode_escape')}  #显示中文，只适用于json
        except Exception:
            print(u'【Error】：您输入的数据格式有误！')
            # traceback.print_exc()
            fomated_body_list = {"json_str": '【Error】：您输入的数据格式有误！',
                                 "json_dict":'【Error】：您输入的数据格式有误！'}

        return HttpResponse(json.dumps(fomated_body_list), content_type='application/json')

#=============================================================== all ===============================================================

@login_required()
def interface_page(req,modules):
    if(modules != 'suit'):
        interfaces = interfaces_oeasy.objects.filter(module=modules).order_by('order').all()
        # csrf
        c = csrf(req)
        c.update({'interfaces': interfaces})
        return render_to_response("interface_"+modules+".html",c)
    else:
        # 全部接口
        suits = suit.objects.all().order_by('orders')
        interfaces_all = interfaces_oeasy.objects.filter( Q(module='public') | Q(module='wyyy') | Q(module='djmj') | Q(module='edcc') | Q(module='dssj') | Q(module='snxm') | Q(module='zhxy')).order_by('-module','order')
        # 分页
        paginator = Paginator(suits, 12)  # 生成paginator对象,设置每页显示n条记录
        num = len(suits)
        page = req.GET.get('page', 1)  # 获取当前的页码数,默认为第1页
        try:
            page_list = paginator.page(page)  # 获取当前页码数的记录列表
        except PageNotAnInteger:
            page_list = paginator.page(1)  # 如果输入的页数不是整数则显示第1页的内容
        except EmptyPage:
            page_list = paginator.page(paginator.num_pages)     #如果输入的页数不在系统的页数中则显示最后一页的内容
        # csrf
        c = csrf(req)
        c.update({'page_list': page_list, 'num': num, 'interfaces_all':interfaces_all})
        return render_to_response("interface_suit.html",c)

#==弹出新建页面
@login_required()
def show_add_window(req,module):
    head_dict = {'Cookie':'','Accept':'','Content-Type':''}
    head_json = json.dumps(head_dict, sort_keys=True, indent=8).encode().decode('raw_unicode_escape')
    public_list = public_para1.objects.exclude(module='suit').filter(~Q(keywords__icontains='AI'))
    # csrf
    c = csrf(req)
    c.update({'module': module,'head_json': head_json,'public_list': public_list})
    return render_to_response("add_interface.html",c)

#==添加接口
def add_interfaces(req,modules):
    if req.method == "POST":
        add_name = req.POST.get('add_name','')
        add_url = req.POST.get('add_url','')
        formated_dict = req.POST.get('formated_dict','')
        add_order = req.POST.get('add_order','')
        add_creator = req.POST.get('add_creator','')
        add_head = req.POST.get('head','')
        add_mode = req.POST.get('mode','')
        add_cookie = req.POST.get('add_cookie','')
        body_format = req.POST.get('body_format','')

        # 接口返回值 - 参数名称
        resp_add_name = req.POST.getlist('resp_add_name','')

        assert_head1 = {'Cookie':'','Accept':'','Content-Type':''}

        if('Error' not in formated_dict and formated_dict != ''):
            # add_head
            add_head = eval(add_head)
            for rec in list(add_head.keys()):
                if(add_head[rec] == ''):
                    del add_head[rec]

            # 接口测试
            if(modules in ('public','wyyy','djmj','edcc','dssj','snxm','zhxy')):
                base_info1 = interfaces_oeasy(name=add_name,url=add_url,head=add_head,body=formated_dict,body_format=body_format,mode=add_mode,order=add_order,charger=add_creator,module=modules,update_cookie=add_cookie,assert_head=assert_head1,assert_mode='',assert_keywords='',assert_body_format='0',assert_body='{}',assert_keywords_is_contain='1',assert_url='',assert_use_new='',assert_keywords_old='',assert_use_new_AI='',assert_url_AI='',assert_head_AI='',assert_mode_AI='',assert_body_format_AI='0',assert_body_AI='{}',assert_keywords_is_contain_AI='1',assert_keywords_new_AI='',assert_keywords_old_AI='')
                base_info1.save()
                print(base_info1,' insert success!')

                if(resp_add_name != ['']):
                    resp_add_keywords = req.POST.getlist('resp_add_keywords','')
                    resp_add_left = req.POST.getlist('resp_add_left','')
                    resp_add_right = req.POST.getlist('resp_add_right','')
                    resp_add_index = req.POST.getlist('resp_add_index','')

                    tmp_list = interfaces_oeasy.objects.aggregate(Max('id'))
                    max_id = tmp_list['id__max']    #已经先执行了插入，所以max_id不需要加1了

                    for i in range(len(resp_add_name)):
                        resp_info1 = public_para1(name=resp_add_name[i],keywords=resp_add_keywords[i],value='',left=resp_add_left[i],right=resp_add_right[i],index=resp_add_index[i],module=modules,module_id=max_id,type='接口返回值')
                        resp_info1.save()
                        print(resp_info1,' insert success!')

                return HttpResponseRedirect('/show_add_window/'+modules+'/')
            # enumeration、xss
            elif(modules in ('enumeration','xss')):
                base_info1 = interfaces_oeasy(name=add_name,url=add_url,head=add_head,body=formated_dict,mode=add_mode,order=add_order,body_format=body_format,module=modules)
                base_info1.save()
                print(base_info1,' insert success!')
                return HttpResponseRedirect('/security/'+modules+'/')
        else:
            return HttpResponse(u'参数错误，请点击浏览器【后退】按钮继续编辑！')

#==弹出编辑页面
@login_required()
def show_edit_interface(req,edit_id,module):
    interface_list_tmp = interfaces_oeasy.objects.filter(id=edit_id)
    interface_list = interface_list_tmp[0]
    # head
    head1 = eval(interface_list.head)
    tmp_head = {'Accept':'','Content-Type':'','Cookie':''}
    tmp = ['Accept','Content-Type','Cookie']
    for rec in tmp:
        if(rec in list(head1.keys())):
            tmp_head[rec] = head1[rec]
    print(eval(json.dumps(eval(interface_list.body), sort_keys=True)))
    # mode
    mode = interface_list.mode
    if(mode == ''):
        mode = 'false'  #必须传一个值，否则传给js为空时会报错，就传false，正好匹配js的false
    # update_cookie
    update_cookie = interface_list.update_cookie

    para_dict = json.dumps(eval(interface_list.body), sort_keys=True).encode().decode('raw_unicode_escape')    # 显示中文，只适用于json
    para_str = json.dumps(eval(interface_list.body), sort_keys=True, indent=8).encode().decode('raw_unicode_escape')   # 显示中文，只适用于json
    head = json.dumps(tmp_head, sort_keys=True, indent=8).encode().decode('raw_unicode_escape')     # 显示中文，只适用于json

    # body_format
    body_format = interface_list.body_format
    if(body_format == ''):
        body_format = 'false'  #必须传一个值，否则传给js为空时会报错，就传false，正好匹配js的false

    # 关键字列表
    public_list_all = public_para1.objects.exclude(module='suit').filter(~Q(keywords__icontains='AI'))

    # 接口返回值列表
    public_list_resp = public_para1.objects.filter(module_id=int(edit_id)).exclude(module='suit')
    flag_resp = 'false'
    if(str(public_list_resp) != '[]'):
        flag_resp = 'true'
    # 如果使用回调，则左右边界必须转义：rec.left.replace("'","&apos;").replace('"','&quot;'))     #html转义单引号和双引号，是在value中能够正常显示

    # csrf
    c = csrf(req)
    c.update({'edit_id': edit_id,'module': module,'mode': mode,'body_format': body_format,'update_cookie': update_cookie,'interface_list_tmp': interface_list_tmp,'head': head,'para_dict': para_dict,'para_str': para_str,'public_list_all': public_list_all,'public_list_resp': public_list_resp,'flag_resp': flag_resp})
    return render_to_response("edit_interface.html",c)

#==保存接口
def save_edit_interface(req,edit_id,modules):
    if req.method == "POST":
        edit_name = req.POST.get('edit_name','')
        edit_url = req.POST.get('edit_url','')
        formated_dict = req.POST.get('formated_dict','')
        edit_order = req.POST.get('edit_order','')
        edit_creator = req.POST.get('edit_creator','')
        edit_head = req.POST.get('head','')
        edit_mode = req.POST.get('mode','')
        edit_cookie = req.POST.get('edit_cookie','')
        body_format = req.POST.get('body_format','')

        # 接口返回值 - 参数名称
        resp_edit_name = req.POST.getlist('resp_edit_name','')

        if('Error' not in formated_dict and formated_dict != ''):
            # edit_head
            edit_head = eval(edit_head)
            for rec in list(edit_head.keys()):
                if(edit_head[rec] == ''):
                    del edit_head[rec]
            # 接口测试
            interface_status1 = ''
            if(modules in ('public','wyyy','djmj','edcc','dssj','snxm','zhxy')):
                # 清空assert_use_new_AI的状态，下次重新编辑新的请求参数的AI断言
                interface_status1 = interfaces_oeasy.objects.filter(id=edit_id).update(name=edit_name,url=edit_url,order=edit_order,charger=edit_creator,body=formated_dict,head=edit_head,mode=edit_mode,module=modules,update_cookie=edit_cookie,body_format=body_format,assert_use_new_AI='')
                print(interface_status1, ' update success!')

                # del public_para1
                public_para1.objects.filter(module_id=int(edit_id)).exclude(module='suit').delete()   #一定要转成int才能查出来，奇葩
                print('module_id = ',edit_id,' delete success!')

                # insert public_para1
                if(resp_edit_name != ['']):
                    resp_edit_keywords = req.POST.getlist('resp_edit_keywords','')
                    resp_edit_left = req.POST.getlist('resp_edit_left','')
                    resp_edit_right = req.POST.getlist('resp_edit_right','')
                    resp_edit_index = req.POST.getlist('resp_edit_index','')

                    for i in range(len(resp_edit_name)):
                        resp_info1 = public_para1(name=resp_edit_name[i],keywords=resp_edit_keywords[i],value='',left=resp_edit_left[i],right=resp_edit_right[i],index=resp_edit_index[i],module=modules,module_id=edit_id,type='接口返回值')
                        resp_info1.save()
                        print(resp_info1,' insert success!')

                return HttpResponseRedirect('/show_edit_interface/'+edit_id+'/'+modules+'/')
            # enumeration、xss
            elif(modules in ('enumeration','xss','app_ddos')):
                interface_status1 = interfaces_oeasy.objects.filter(id=edit_id).update(name=edit_name,url=edit_url,order=edit_order,charger=edit_creator,body=formated_dict,head=edit_head,mode=edit_mode,module=modules,body_format=body_format)
                print(interface_status1,' update success!')
                return HttpResponseRedirect('/security/'+edit_id+'/'+modules+'/')
        else:
            return HttpResponse(u'参数错误，请点击浏览器【后退】按钮继续编辑！')

#==编辑断言
@login_required()
def show_assert(req,edit_id):
    assert_list = interfaces_oeasy.objects.filter(id=edit_id)
    # is_new
    is_new = assert_list[0].assert_use_new
    if(is_new == ''):
        is_new = 'false'
    # head
    head = eval(assert_list[0].assert_head)
    tmp_head = {'Accept':'','Content-Type':'','Cookie':''}
    tmp = ['Accept','Content-Type','Cookie']
    for rec in tmp:
        if(rec in list(head.keys())):
            tmp_head[rec] = head[rec]
    head1 = json.dumps(tmp_head, sort_keys=True, indent=8).encode().decode('raw_unicode_escape')
    # mode
    mode = assert_list[0].assert_mode
    if(mode == ''):
        mode = 'false'
    # is_contain
    is_contain = assert_list[0].assert_keywords_is_contain
    if(is_contain == ''):
        is_contain = 'false'
    # body
    body = assert_list[0].assert_body
    print(body)
    para_dict = json.dumps(eval(body), sort_keys=True).encode().decode('raw_unicode_escape')    # 显示中文，只适用于json
    para_str = json.dumps(eval(body), sort_keys=True, indent=8).encode().decode('raw_unicode_escape')   # 显示中文，只适用于json

    # assert_body_format
    assert_body_format = assert_list[0].assert_body_format
    if(assert_body_format == ''):
        assert_body_format = 'false'  #必须传一个值，否则传给js为空时会报错，就传false，正好匹配js的false

    public_list = public_para1.objects.exclude(module='suit').filter(~Q(keywords__icontains='AI'))

    # csrf
    c = csrf(req)
    c.update({'edit_id': edit_id,'is_new': is_new,'assert_list': assert_list,'mode': mode,'assert_body_format': assert_body_format,'is_contain': is_contain,'head1': head1,'para_dict': para_dict,'para_str': para_str,'public_list': public_list})
    return render_to_response("assert_interface.html",c)

#==保存断言
def save_assert(req,edit_id):
    if req.method == "POST":
        is_new = req.POST.get('is_new','')
        assert_url = req.POST.get('assert_url','')
        assert_head = req.POST.get('head','')
        assert_mode = req.POST.get('mode','')
        is_contain = req.POST.get('is_contain','')
        assert_keywords = req.POST.get('assert_keywords','')
        assert_keywords_old = req.POST.get('assert_keywords_old','')
        formated_dict = req.POST.get('formated_dict','')
        assert_body_format = req.POST.get('assert_body_format','')

        if('Error' not in formated_dict and formated_dict != ''):
            # update assert_info
            assert_head1 = eval(assert_head)
            for rec in list(assert_head1.keys()):
                if (assert_head1[rec] == ''):
                    del assert_head1[rec]
            assert_status1 = interfaces_oeasy.objects.filter(id=edit_id).update(assert_url=assert_url,assert_head=assert_head1,assert_mode=assert_mode,assert_body_format=assert_body_format,assert_body=formated_dict,assert_keywords=assert_keywords,assert_keywords_is_contain=is_contain,assert_use_new=is_new,assert_keywords_old=assert_keywords_old)

            print(assert_status1, ' update success!')
            return HttpResponseRedirect('/show_assert/'+edit_id+'/')
        else:
            return HttpResponse(u'参数错误，请点击浏览器【后退】按钮继续编辑！')

#==删除接口
def del_interface(req):
    if req.method == "POST":
        raw_data = req.body
        raw_data = json.loads(raw_data)
        id1 = raw_data['id1']

        # del
        interfaces_oeasy.objects.filter(id=id1).delete()
        print('id = ',id1,' delete success!')
        public_para1.objects.filter(module_id=int(id1)).exclude(module='suit').delete()   #一定要转成int才能查出来，奇葩
        print('module_id = ',id1,' delete success!')
        return HttpResponse('delete success!')

def start_interface_test(req):
    if req.method == "POST":
        raw_data = req.body
        raw_data = json.loads(raw_data)
        id1 = raw_data['id1']

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
        public_list2 = public_para1.objects.exclude(module='pub').exclude(module='suit').filter(~Q(keywords__icontains='AI'))
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

        interfaces = interfaces_oeasy.objects.filter(id=id1)[0]
        print_log('interface_id: ',','),print_log(id1)

        # 映射url
        url = interfaces.url
        if("{" in url and "}" in url):
            end_index = url.find("}")
            key_url = url[:end_index+1]
            url = url.replace(key_url,public_dict[key_url.replace('{','').replace('}','')])

        # 映射head
        head = eval(interfaces.head)
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
        body = eval(interfaces.body)
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

        mode = interfaces.mode
        body_format = interfaces.body_format

        # 测试开始
        response,cookie = interface_test_start(url,body,head,mode,body_format,True)     #False，不打印日志；True，打印日志

        # 更新cookie
        update_cookie = interfaces.update_cookie
        if('{' in update_cookie and '}' in update_cookie):
            for rec in keyword_list1:
                if(rec == update_cookie):
                    cookie_status1 = public_para1.objects.filter(keywords=rec.replace('{','').replace('}','')).update(value=cookie)
                    print(cookie_status1, ' update success!')
                    break

        # 返回值存入缓存，保留30秒
        public_resp = public_para1.objects.filter(module_id=int(id1)).exclude(module='suit')
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
                    print_log('\n接口返回关键字： '+rec.keywords+'，匹配第'+str(index+1)+'个        '+left+right+'       ，值为：'+result)
                except Exception:
                    print((rec.keywords,left,right,index),' 在返回结果中未匹配到')

        # 断言
        is_new = interfaces.assert_use_new
        if(is_new == '1'):
            assert_url = interfaces.assert_url
            assert_head = eval(interfaces.assert_head)
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
            assert_mode = interfaces.assert_mode
            assert_body = eval(interfaces.assert_body)
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
            assert_keywords = interfaces.assert_keywords
            # 映射assert_keywords
            # 替换关键字
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
            is_contain = interfaces.assert_keywords_is_contain
            # assert_body_format
            assert_body_format = interfaces.assert_body_format
            # assert start
            assert_test(assert_url,assert_head,assert_mode,assert_body,assert_keywords,is_contain,assert_body_format,True)
        else:
            # assert_keywords_old
            assert_keywords_old = interfaces.assert_keywords_old
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
            assert_test_old(response,assert_keywords_old,True)

        #==日志
        File = '/autotest_platform/test_out.log'
        File1 = open(File,'r',encoding='utf-8')
        test_log = File1.readlines()
        #==去掉test_log中的'<>'，否则textarea中无法看到输出结果
        test_log = str(test_log)
        test_log = test_log.replace('<','[').replace('>',"]")
        test_log = eval(test_log)
        return HttpResponse(test_log)

def start_interface_test_bak(req):
    if req.method == "POST":
        raw_data = req.body
        raw_data = json.loads(raw_data)
        id1 = raw_data['id1']

        #==cookie
        public_para_tmp = public_para.objects.all()[0]
        Cookie_dict = {'yypt': public_para_tmp.yypt,
                       'wypt': public_para_tmp.wypt,
                       'yhsq': public_para_tmp.yhsq,
                       'wyj': public_para_tmp.wyj,
                       'dspt': public_para_tmp.dspt,
                       'sjpt': public_para_tmp.sjpt,
                       'ggpt': public_para_tmp.ggpt,
                       'xqmc': public_para_tmp.xqmc}

        #==清空日志文件
        f_handler = open('/autotest_platform/test_out.log', 'w')
        f_handler.truncate()
        f_handler.close()

        interfaces = interfaces_oeasy.objects.filter(id=id1)[0]
        print_log('interface_id: ',','),print_log(id1)
        url = interfaces.url

        # 映射head
        head = eval(interfaces.head)
        if(head != {} and 'Cookie' in list(head.keys())):
            for rec1 in list(Cookie_dict.keys()):
                if(head['Cookie'] == rec1):
                    head['Cookie'] = str(Cookie_dict[rec1])
        print(head)
        # 映射body
        body = eval(interfaces.body)
        for rec1 in list(body.keys()):
            if (body[rec1] == u'xqmc'):
                body[rec1] = str(Cookie_dict['xqmc'])
            elif ('xqmc' in body[rec1] and (body[rec1] != u'xqmc') and ('select' not in body[rec1])):
                body[rec1] = body[rec1].replace('xqmc', str(Cookie_dict['xqmc']))
            elif ('xqid' in body[rec1]):
                sql = 'select * from basedata.t_base_unit where `name`="' + str(Cookie_dict['xqmc']) + '"'
                cursor = connection.cursor()
                cursor.execute(sql)
                data = cursor.fetchall()
                xqid = data[0][0]
                body[rec1] = body[rec1].replace('xqid', str(xqid))
            elif (body[rec1] == u'yhsq'):
                body[rec1] = str(Cookie_dict['yhsq'])
            elif (body[rec1] == u'wyj'):
                body[rec1] = str(Cookie_dict['wyj'])
            elif('select' in body[rec1]):
                sql = body[rec1]
                if('xqmc' in body[rec1]):       #替换xqid
                    sql = body[rec1].replace('xqmc',str(Cookie_dict['xqmc']))
                cursor = connection.cursor()
                print(sql)
                cursor.execute(sql)
                data = cursor.fetchall()
                print(u'查询的id为： ',data[0][0])
                body[rec1] = data[0][0]
        print(body)

        mode = interfaces.mode
        body_format = 'NOT_JSON'

        # 测试开始
        response = interface_test_start(url,body,head,mode,body_format,True)    #False，不打印日志；True，打印日志

        # 断言
        is_new = interfaces.assert_use_new
        if(is_new == 1):
            assert_url = interfaces.assert_url
            assert_head = eval(interfaces.assert_head)
            # 映射assert_head
            if(assert_head != {} and 'Cookie' in list(head.keys())):
                for rec1 in list(Cookie_dict.keys()):
                    if(assert_head['Cookie'] == rec1):
                        assert_head['Cookie'] = str(Cookie_dict[rec1])
            # assert_mode
            assert_mode = interfaces.assert_mode
            assert_body = eval(interfaces.assert_body)
            # 映射assert_body
            for rec1 in list(assert_body.keys()):
                if (assert_body[rec1] == u'xqmc'):
                    assert_body[rec1] = str(Cookie_dict['xqmc'])
                elif ('xqmc' in assert_body[rec1] and (assert_body[rec1] != u'xqmc') and ('select' not in assert_body[rec1])):
                    assert_body[rec1] = assert_body[rec1].replace('xqmc', str(Cookie_dict['xqmc']))
                elif ('xqid' in assert_body[rec1]):
                    sql = 'select * from basedata.t_base_unit where `name`="' + str(Cookie_dict['xqmc']) + '"'
                    cursor = connection.cursor()
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    xqid = data[0][0]
                    assert_body[rec1] = assert_body[rec1].replace('xqid', str(xqid))
                elif (assert_body[rec1] == u'yhsq'):
                    assert_body[rec1] = str(Cookie_dict['yhsq'])
                elif (assert_body[rec1] == u'wyj'):
                    assert_body[rec1] = str(Cookie_dict['wyj'])
                elif('select' in assert_body[rec1]):
                    sql = assert_body[rec1]
                    if('xqmc' in assert_body[rec1]):       #替换xqid
                        sql = assert_body[rec1].replace('xqmc',str(Cookie_dict['xqmc']))
                    cursor = connection.cursor()
                    print(sql)
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    print(u'查询的id为： ',data[0][0])
                    assert_body[rec1] = data[0][0]
            print(assert_body)
            # assert_keywords
            assert_keywords = interfaces.assert_keywords
            # 映射assert_keywords
            if (assert_keywords == u'xqmc'):
                assert_keywords = str(Cookie_dict['xqmc'])
            elif ('xqmc' in assert_keywords and (assert_keywords != u'xqmc') and ('select' not in assert_keywords)):
                assert_keywords = assert_keywords.replace('xqmc', str(Cookie_dict['xqmc']))
            elif ('xqid' in assert_keywords):
                sql = 'select * from basedata.t_base_unit where `name`="' + str(Cookie_dict['xqmc']) + '"'
                cursor = connection.cursor()
                cursor.execute(sql)
                data = cursor.fetchall()
                xqid = data[0][0]
                assert_keywords = assert_keywords.replace('xqid', str(xqid))
            elif (assert_keywords == u'yhsq'):
                assert_keywords = str(Cookie_dict['yhsq'])
            elif (assert_keywords == u'wyj'):
                assert_keywords = str(Cookie_dict['wyj'])
            elif ('select' in assert_keywords):
                sql = assert_keywords
                if ('xqmc' in assert_keywords):  # 替换xqid
                    sql = assert_keywords.replace('xqmc', str(Cookie_dict['xqmc']))
                cursor = connection.cursor()
                print(sql)
                cursor.execute(sql)
                data = cursor.fetchall()
                print(u'查询的id为： ', data[0][0])
                assert_keywords = data[0][0]
            # is_contain
            is_contain = interfaces.assert_keywords_is_contain
            # assert start
            assert_test(assert_url,assert_head,assert_mode,assert_body,assert_keywords,is_contain,body_format,True)
        else:
            # assert_keywords_old
            assert_keywords_old = interfaces.assert_keywords_old
            # assert start
            assert_test_old(response,assert_keywords_old,True)

        #==日志
        File = '/autotest_platform/test_out.log'
        File1 = open(File,'r',encoding='utf-8')
        test_log = File1.readlines()
        #==去掉test_log中的'<>'，否则textarea中无法看到输出结果
        test_log = str(test_log)
        test_log = test_log.replace('<','[').replace('>',"]")
        test_log = eval(test_log)
        return HttpResponse(test_log)

#=============================================================== AI ===============================================================

#==编辑断言AI
@login_required()
def show_assert_AI(req,edit_id):
    assert_list = interfaces_oeasy.objects.filter(id=edit_id)
    # is_new_AI
    is_new_AI = assert_list[0].assert_use_new_AI
    if(is_new_AI == ''):    #没有AI数据的情况
        is_new_AI = 'false'
        # is_new
        is_new = assert_list[0].assert_use_new
        if(is_new == ''):
            is_new = 'false'
        # head
        head = eval(assert_list[0].assert_head)
        tmp_head = {'Accept':'','Content-Type':'','Cookie':''}
        tmp = ['Accept','Content-Type','Cookie']
        for rec in tmp:
            if(rec in list(head.keys())):
                tmp_head[rec] = head[rec]
        head1 = json.dumps(tmp_head, sort_keys=True, indent=8).encode().decode('raw_unicode_escape')
        # mode
        mode = assert_list[0].assert_mode
        if(mode == ''):
            mode = 'false'
        # is_contain
        is_contain = assert_list[0].assert_keywords_is_contain
        if(is_contain == ''):
            is_contain = 'false'
        # body
        body = assert_list[0].assert_body
        para_dict = json.dumps(eval(body), sort_keys=True).encode().decode('raw_unicode_escape')    # 显示中文，只适用于json
        para_str = json.dumps(eval(body), sort_keys=True, indent=8).encode().decode('raw_unicode_escape')   # 显示中文，只适用于json

        # assert_body_format_AI
        assert_body_format_AI = assert_list[0].assert_body_format_AI
        if(assert_body_format_AI == ''):
            assert_body_format_AI = 'false'  #必须传一个值，否则传给js为空时会报错，就传false，正好匹配js的false

        public_list = public_para1.objects.exclude(module='suit').filter(~Q(keywords__icontains='AI'))

        # AI
        para_list = eval(assert_list[0].body).keys()
        new_AI_list = old_AI_list = public_para1.objects.filter(Q(keywords__icontains='AI')).values('name').annotate(tt=Count('name'))
        L_AI = len(new_AI_list)
    else:       #有AI数据的情况
        # is_new
        is_new = assert_list[0].assert_use_new_AI
        if(is_new == ''):
            is_new = 'false'
        # head
        head = eval(assert_list[0].assert_head_AI)
        tmp_head = {'Accept':'','Content-Type':'','Cookie':''}
        tmp = ['Accept','Content-Type','Cookie']
        for rec in tmp:
            if(rec in list(head.keys())):
                tmp_head[rec] = head[rec]
        head1 = json.dumps(tmp_head, sort_keys=True, indent=8).encode().decode('raw_unicode_escape')
        # mode
        mode = assert_list[0].assert_mode_AI
        if(mode == ''):
            mode = 'false'
        # is_contain
        is_contain = assert_list[0].assert_keywords_is_contain_AI
        if(is_contain == ''):
            is_contain = 'false'
        # body
        body = assert_list[0].assert_body_AI
        para_dict = json.dumps(eval(body), sort_keys=True).encode().decode('raw_unicode_escape')    # 显示中文，只适用于json
        para_str = json.dumps(eval(body), sort_keys=True, indent=8).encode().decode('raw_unicode_escape')   # 显示中文，只适用于json
        print(para_str)

        # assert_body_format_AI
        assert_body_format_AI = assert_list[0].assert_body_format_AI
        if(assert_body_format_AI == ''):
            assert_body_format_AI = 'false'  #必须传一个值，否则传给js为空时会报错，就传false，正好匹配js的false

        public_list = public_para1.objects.exclude(module='suit').filter(~Q(keywords__icontains='AI'))

        # AI
        para_list = eval(assert_list[0].body).keys()    #没用，为了后面模板传值暂时保留
        AI_list = public_para1.objects.filter(Q(keywords__icontains='AI')).values('name').annotate(tt=Count('name'))
        L_AI = len(AI_list)
        # new
        tmp_new_AI_list = assert_list[0].assert_keywords_new_AI
        new_AI_list = []
        for rec1 in eval(tmp_new_AI_list).keys():
            value = eval(tmp_new_AI_list)[rec1]
            for i in range(len(value)):
                new_AI_list.append((rec1,AI_list[i]['name'],value[i]))  #(para,AI,value)
        # old
        tmp_old_AI_list = assert_list[0].assert_keywords_old_AI
        old_AI_list = []
        for rec1 in eval(tmp_old_AI_list).keys():
            value = eval(tmp_old_AI_list)[rec1]
            for i in range(len(value)):
                old_AI_list.append((rec1,AI_list[i]['name'],value[i]))

    # csrf
    c = csrf(req)
    c.update({'edit_id': edit_id,'is_new': is_new,'assert_list': assert_list,'mode': mode,'assert_body_format_AI': assert_body_format_AI,'is_contain': is_contain,'head1': head1,'para_dict': para_dict,'para_str': para_str,'public_list': public_list,'para_list': para_list,'is_new_AI': is_new_AI,'new_AI_list': new_AI_list,'old_AI_list': old_AI_list,'L_AI': L_AI})
    return render_to_response("assert_interface_AI.html",c)

#==保存断言AI
def save_assert_AI(req,edit_id):
    if req.method == "POST":
        is_new = req.POST.get('is_new','')
        assert_url = req.POST.get('assert_url','')
        assert_head = req.POST.get('head','')
        assert_mode = req.POST.get('mode','')
        is_contain = req.POST.get('is_contain','')
        formated_dict = req.POST.get('formated_dict','')
        assert_body_format_AI = req.POST.get('assert_body_format_AI','')

        if('Error' not in formated_dict and formated_dict != ''):
            assert_list = interfaces_oeasy.objects.filter(id=edit_id)
            para_list = eval(assert_list[0].body).keys()
            # new
            assert_keywords_new = {}
            for rec in para_list:
                tmp_para_list = req.POST.getlist('new_'+rec,'')
                print_log(tmp_para_list)
                tmp_value_list = []
                for rec1 in tmp_para_list:
                    tmp_value_list.append(rec1)
                assert_keywords_new[rec] = tmp_value_list
            print(assert_keywords_new)
            # old
            assert_keywords_old = {}
            for rec in para_list:
                tmp_para_list = req.POST.getlist('old_'+rec,'')
                tmp_value_list = []
                for rec1 in tmp_para_list:
                    tmp_value_list.append(rec1)
                assert_keywords_old[rec] = tmp_value_list
            print(assert_keywords_old)
            # head
            assert_head1 = eval(assert_head)
            for rec in list(assert_head1.keys()):
                if (assert_head1[rec] == ''):
                    del assert_head1[rec]
            # update assert_info
            assert_status1 = interfaces_oeasy.objects.filter(id=edit_id).update(assert_url_AI=assert_url,assert_head_AI=assert_head1,assert_mode_AI=assert_mode,assert_body_format_AI=assert_body_format_AI,assert_body_AI=formated_dict,assert_keywords_is_contain_AI=is_contain,assert_use_new_AI=is_new,assert_keywords_new_AI=assert_keywords_new,assert_keywords_old_AI=assert_keywords_old)

            print(assert_status1, ' update success!')
            return HttpResponseRedirect('/show_assert_AI/'+edit_id+'/')
        else:
            return HttpResponse(u'参数错误，请点击浏览器【后退】按钮继续编辑！')

def start_interface_test_AI(req):
    if req.method == "POST":
        raw_data = req.body
        raw_data = json.loads(raw_data)
        id1 = raw_data['id1']
        num = int(raw_data['num'])

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
        public_list2 = public_para1.objects.exclude(module='pub').exclude(module='suit').filter(~Q(keywords__icontains='AI'))
        keyword_list2 = ["{"+rec.keywords+"}" for rec in public_list2]
        public_dict2 = {}
        for rec in public_list2:
            public_dict2[rec.keywords] = str((rec.left,rec.right,rec.index))

        #==公共参数 - dict - all
        public_dict = {}
        public_dict.update(public_dict1)
        public_dict.update(public_dict2)

        #==清空日志文件
        # 一次性增加textarea
        if(num == 0):
            f_handler = open('/autotest_platform/test_out.log', 'w')
            f_handler.truncate()
            f_handler.close()
        # # 递归增加textarea
        # f_handler = open('/autotest_platform/test_out.log', 'w')
        # f_handler.truncate()
        # f_handler.close()

        interfaces = interfaces_oeasy.objects.filter(id=id1)[0]

        #================================== AI处理 ==================================

        # 获取当前AI测试的参数cur_para
        is_new = interfaces.assert_use_new_AI
        if(is_new == '1'):
            assert_keywords_dict = interfaces.assert_keywords_new_AI
            # assert_keywords_new
            assert_keywords_list = []
            for rec in eval(assert_keywords_dict).keys():
                assert_keywords_list += eval(assert_keywords_dict)[rec]
            assert_keywords = assert_keywords_list[num]
        else:
            assert_keywords_dict = interfaces.assert_keywords_old_AI
            # assert_keywords
            assert_keywords_list = []
            for rec in eval(assert_keywords_dict).keys():
                assert_keywords_list += eval(assert_keywords_dict)[rec]
            assert_keywords = assert_keywords_list[num]
        para_list = []
        for rec in eval(assert_keywords_dict).keys():
            value = eval(assert_keywords_dict)[rec]
            for rec1 in value:
                para_list.append(rec)
        # cur_para
        cur_para = para_list[num]

        # 获取当前AI公共参数cur_AI_name，cur_AI_value
        tmp_AI_list = public_para1.objects.filter(Q(keywords__icontains='AI')).values('name').annotate(tt=Count('name'))
        AI_list = []
        for rec in tmp_AI_list:
            AI_list.append(rec['name'])
        L = len(eval(assert_keywords_dict).keys())
        AI_list = AI_list * L
        # sum
        sum = len(AI_list) - 1
        # cur_AI_name
        cur_AI_name = AI_list[num]

        List1 = public_para1.objects.filter(name=cur_AI_name)
        List2 = []
        for rec in List1:
            List2.append(rec.value)
        # cur_AI_value
        cur_AI_value = random.sample(List2,1)[0]

        #================================== 处理完毕 ==================================

        if(assert_keywords != ''):
            # 映射url
            url = interfaces.url
            if("{" in url and "}" in url):
                end_index = url.find("}")
                key_url = url[:end_index+1]
                url = url.replace(key_url,public_dict[key_url.replace('{','').replace('}','')])

            # 映射head
            head = eval(interfaces.head)
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
            body = eval(interfaces.body)
            for rec in body.keys():
                # 替换要AI测试的参数
                if(rec == cur_para):
                    body[rec] = cur_AI_value
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

            mode = interfaces.mode
            body_format = interfaces.body_format

            # 测试开始
            response,cookie = interface_test_start(url,body,head,mode,body_format,False)    #False，不打印日志；True，打印日志

            # 更新cookie
            update_cookie = interfaces.update_cookie
            if('{' in update_cookie and '}' in update_cookie):
                for rec in keyword_list1:
                    if(rec == update_cookie):
                        cookie_status1 = public_para1.objects.filter(keywords=rec.replace('{','').replace('}','')).update(value=cookie)
                        print(cookie_status1, ' update success!')
                        break

            # 返回值存入缓存，保留30秒
            public_resp = public_para1.objects.filter(module_id=int(id1)).exclude(module='suit')
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
                        print_log('\n接口返回关键字： '+rec.keywords+'，匹配第'+str(index+1)+'个        '+left+right+'       ，值为：'+result)
                    except Exception:
                        print((rec.keywords,left,right,index),' 在返回结果中未匹配到')

            print_log('当前参数：  ',',')
            print_log(cur_para)
            print_log('数据模型：  ',',')
            print_log(cur_AI_name.replace('AI - ',''))
            print_log('测试字符：  ',',')
            print_log(cur_AI_value)
            print_log('接口返回：  ',',')
            print_log(response)

            # 断言
            is_new = interfaces.assert_use_new_AI
            if(is_new == '1'):
                assert_url = interfaces.assert_url_AI
                assert_head = eval(interfaces.assert_head_AI)
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
                assert_mode = interfaces.assert_mode_AI
                assert_body = eval(interfaces.assert_body_AI)
                # 映射assert_body
                for rec in assert_body.keys():
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
                # 映射assert_keywords
                # 替换关键字
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
                is_contain = interfaces.assert_keywords_is_contain_AI
                # assert_body_format_AI
                assert_body_format_AI = interfaces.assert_body_format_AI
                # assert start
                assert_test(assert_url,assert_head,assert_mode,assert_body,assert_keywords,is_contain,assert_body_format_AI,False)   #False，AI测试使用；True，其他测试使用
            else:
                # 替换关键字
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
                # assert start
                assert_test_old(response,assert_keywords,False)

        #==日志
        File = '/autotest_platform/test_out.log'
        File1 = open(File,'r',encoding='utf-8')
        test_log = File1.readlines()
        #==去掉test_log中的'<>'，否则textarea中无法看到输出结果
        test_log = str(test_log)
        test_log = test_log.replace('<','[').replace('>',"]")
        test_log = eval(test_log)

        result_json = {'test_log': test_log,
                       'sum': sum
                       }

        return HttpResponse(json.dumps(result_json), content_type='application/json')

#=============================================================== suit ===============================================================

#==已废弃
@login_required()
def suit_page(request):
    # #==接口
    # suits = suit.objects.all()
    # print suits

    # 全部接口
    cursor = connection.cursor()
    # 接口
    # cursor.execute("select t1.*,group_concat(t2.id) as interface_id from app_interface_suit t1,app_interface_suit_interface t2 where t1.id=t2.suit_id GROUP BY suit_id;")
    cursor.execute("select * from app_interface_suit order by orders;")
    suits = cursor.fetchall()
    # 全部接口
    cursor.execute("select 'public' as table_name,id,`name`,url,`order` from app_interface_public union all "
                   "select 'wyyy' as table_name,id,`name`,url,`order` from app_interface_wyyy union all "
                   "select 'djmj' as table_name,id,`name`,url,`order` from app_interface_djmj union all "
                   "select 'edcc' as table_name,id,`name`,url,`order` from app_interface_edcc union all "
                   "select 'ggpt' as table_name,id,`name`,url,`order` from app_interface_ggpt order by table_name,`order`")
    interfaces_all = cursor.fetchall()
    # csrf
    c = csrf(request)
    c.update({'suits': suits, 'interfaces_all':interfaces_all})
    return render_to_response("interface_suit.html",c)

#==添加测试套
def add_suit(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        suit_list = raw_data['suit_list']
        print(suit_list)

        #==interface_name
        interfaces = ''
        interfaces1 = ''
        interface_list = suit_list[2]
        L = len(interface_list)
        for i in range(L):
            name1 = interface_list[i].split('_')[2]
            if(L == 1):
                interfaces += interface_list[i]
                interfaces1 += name1
            elif(L > 1 and (i != L-1)):
                interfaces += interface_list[i] + ','
                interfaces1 += name1 + u' ，'
            elif(L > 1 and (i == L-1)):
                interfaces += interface_list[i]
                interfaces1 += name1
        print(interfaces)
        print(interfaces1)

        #==app_interface_suit
        suit_info1 = suit(suit_name=suit_list[0],charger=suit_list[1],orders=suit_list[3],interface_name=interfaces,interface_name_display=interfaces1)
        suit_info1.save()
        print(suit_info1,' insert success!')

        # #==app_interface_suit_interface
        # interface_list = suit_list[3]
        # for rec in interface_list:
        #     table_name = rec.split('_')[0]
        #     id1 = rec.split('_')[1]
        #     interface_name1 = rec.split('_')[2]
        #
        #     #==para_list
        #     para_list = eval(table_name).objects.filter(id=id1)[0]
        #     url1 = para_list.url
        #     para1 = para_list.para
        #     head1 = para_list.head
        #     body1 = para_list.body
        #     mode1 = para_list.mode
        #     order1 = para_list.order
        #
        #     #==suit_id
        #     suit_id1 = suit.objects.filter(suit_name=suit_list[0])[0].id
        #
        #     #==app_interface_suit_interface
        #     suit_info2 = suit_interface(suit_id=suit_id1,suit_name=suit_list[0],interface_name=interface_name1,url=url1,para=para1,head=head1,body=body1,mode=mode1,order=order1)
        #     suit_info2.save()
        #     print suit_info2,' insert success!'

        return HttpResponse('insert success!')

#==删除测试套
def del_suit(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        id1 = raw_data['id1']

        #==del suit_interface
        suit_interface.objects.filter(suit_id=id1).delete()
        print('suit_interface delete success!')

        #==del suit
        suit.objects.filter(id=id1).delete()
        print('suit delete success!')

        #==del public_para1
        public_para1.objects.filter(module_id=int(id1),module='suit').delete()   #一定要转成int才能查出来，奇葩
        print('module_id = ',id1,' delete success!')

        return HttpResponse('delete success!')

#==编辑测试套
#==已尝试过：1、根据名称获取id_list，但是名称重复就会导致接口参数都一样；2、在接口列表增加序号，但是点击添加行，序号不会自动变化
def show_edit_suit(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        id1 = raw_data['id1']
        suit_name1 = raw_data['suit_name1']
        print(id1,suit_name1)

        #==suit_info
        suit_info = suit.objects.filter(id=id1)[0]

        #==id，解决相同接口不同传参的问题
        #根据名称来显示id，解决了排序的问题
        # tmp_id = suit_interface.objects.filter(suit_id=id1)
        # id_list = [rec.id for rec in tmp_id]
        id_list = []
        tmp_id_list = suit_info.interface_name.split(',')
        for rec in tmp_id_list:
            if(rec.startswith('suit_interface') == True):
                tmp_id = rec.split('_')[2]
            else:
                tmp_id = rec.split('_')[1]
            id_list.append(tmp_id)
        print(id_list)

        #==回调传递json
        suit_info1 = {'id1':id1,
                      'suit_name':suit_info.suit_name,
                      'id_list':id_list,
                      'interface_name':suit_info.interface_name,
                      'charger':suit_info.charger,
                      'orders':suit_info.orders,}

        return HttpResponse(json.dumps(suit_info1), content_type='application/json')

#==删除接口
def del_row1(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        del_id = raw_data['del_id']

        if(del_id != ''):
            suit_interface.objects.filter(id=del_id).delete()
            print('suit_interface delete success!')

        return HttpResponse('delete success!')

#==删除接口
def del_row_edit(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        del_id = raw_data['del_id']

        if(del_id != ''):
            suit_interface.objects.filter(id=del_id).delete()
            print('suit_interface delete success!')

        return HttpResponse('delete success!')

#==保存测试套
def save_edit_suit(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        suit_info = raw_data['suit_info']

        #==interface_name
        interfaces = ''
        interfaces1 = ''
        interface_list = suit_info[3]
        L = len(interface_list)
        for i in range(L):
            tmp_name1 = interface_list[i]
            if(tmp_name1.startswith('suit_interface') == True):
                name1 = interface_list[i].split('_')[3]
            else:
                name1 = interface_list[i].split('_')[2]
            if(L == 1):
                interfaces += interface_list[i]
                interfaces1 += name1
            elif(L > 1 and (i != L-1)):
                interfaces += interface_list[i] + ','
                interfaces1 += name1 + u' ， '
            elif(L > 1 and (i == L-1)):
                interfaces += interface_list[i]
                interfaces1 += name1
        print(interfaces)
        print(interfaces1)

        #==update
        suit_status1 = suit.objects.filter(id=suit_info[0]).update(suit_name=suit_info[1],interface_name=interfaces,interface_name_display=interfaces1,charger=suit_info[2],orders=suit_info[4])
        print(suit_status1,' update success!')

        tmp_list = suit_interface.objects.filter(suit_id=suit_info[0])
        for rec in tmp_list:
            interface_status1 = suit_interface.objects.filter(id=rec.id).update(suit_name=suit_info[1])
            print(interface_status1,' update success!')

        return HttpResponse('update_use_status success!')

#==接口参数
def show_edit_para_suit(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        table_name = raw_data['table_name']
        id1 = raw_data['id1']
        interface_name1 = raw_data['interface_name1']
        id2 = raw_data['id2']
        print(table_name,id1,interface_name1,id2)

        #==id2为空则从table_name里面取参数，否则从suit_interface里取参数
        if(id2 == ''):
            para1 = interfaces_oeasy.objects.filter(id=id1)[0].body
            mode1 = interfaces_oeasy.objects.filter(id=id1)[0].mode
            head1 = interfaces_oeasy.objects.filter(id=id1)[0].head
        elif(id2 != ''):
            para1 = suit_interface.objects.filter(id=id2)[0].body
            mode1 = suit_interface.objects.filter(id=id2)[0].mode
            head1 = suit_interface.objects.filter(id=id2)[0].head

        #head
        head1 = eval(head1)
        tmp_head = {'Accept':'','Content-Type':'','Cookie':''}
        tmp = ['Accept','Content-Type','Cookie']
        for rec in tmp:
            if(rec in list(head1.keys())):
                tmp_head[rec] = head1[rec]

        #==回调传递json
        interface_list1 = {'id1': id1,
                           'para_dict': json.dumps(eval(para1), sort_keys=True).encode().decode('raw_unicode_escape'),    # 显示中文，只适用于json
                           'para_str': json.dumps(eval(para1), sort_keys=True, indent=8).encode().decode('raw_unicode_escape'),   # 显示中文，只适用于json
                           'head': json.dumps(tmp_head, sort_keys=True, indent=8).encode().decode('raw_unicode_escape'),     # 显示中文，只适用于json
                           'mode': mode1}

        return HttpResponse(json.dumps(interface_list1), content_type='application/json')

@login_required()
#==接口参数
def show_edit_suit_interface(req,para):
    if req.method == "GET":
        table_name = para.split('_')[0]
        id1 = para.split('_')[1]
        id2 = para.split('_')[2]
        print(table_name,id1,id2)

        #==id2为空则从table_name里面取参数，否则从suit_interface里取参数
        flag_resp = 'false'
        if(id2 == ''):
            try:
                # body_format
                body_format = interfaces_oeasy.objects.filter(id=id1)[0].body_format
                if(body_format == ''):
                    body_format = 'false'  #必须传一个值，否则传给js为空时会报错，就传false，正好匹配js的false
                para1 = interfaces_oeasy.objects.filter(id=id1)[0].body
                mode1 = interfaces_oeasy.objects.filter(id=id1)[0].mode
                head1 = interfaces_oeasy.objects.filter(id=id1)[0].head
                update_cookie1 = interfaces_oeasy.objects.filter(id=id1)[0].update_cookie
                # 接口返回值列表
                public_list_resp = public_para1.objects.filter(module_id=int(id1)).exclude(module='suit')
                if(str(public_list_resp) != '[]'):
                    flag_resp = 'true'
            except Exception:
                return HttpResponse('您未选择任何接口，请先选择接口！')
        elif(id2 != ''):
            # body_format
            body_format = suit_interface.objects.filter(id=id2)[0].body_format
            if(body_format == ''):
                body_format = 'false'  #必须传一个值，否则传给js为空时会报错，就传false，正好匹配js的false
            para1 = suit_interface.objects.filter(id=id2)[0].body
            mode1 = suit_interface.objects.filter(id=id2)[0].mode
            head1 = suit_interface.objects.filter(id=id2)[0].head
            update_cookie1 = suit_interface.objects.filter(id=id2)[0].update_cookie
            # 接口返回值列表
            public_list_resp = public_para1.objects.filter(module_id=int(id2),module='suit')
            if(str(public_list_resp) != '[]'):
                flag_resp = 'true'

        if(mode1 == ''):
            mode1 = 'false'

        #head
        head1 = eval(head1)
        tmp_head = {'Accept':'','Content-Type':'','Cookie':''}
        tmp = ['Accept','Content-Type','Cookie']
        for rec in tmp:
            if(rec in list(head1.keys())):
                tmp_head[rec] = head1[rec]

        #==回调传递json
        interface_list1 = {'id1': id1,
                           'para_dict': json.dumps(eval(para1), sort_keys=True).encode().decode('raw_unicode_escape'),    # 显示中文，只适用于json
                           'para_str': json.dumps(eval(para1), sort_keys=True, indent=8).encode().decode('raw_unicode_escape'),   # 显示中文，只适用于json
                           'head': json.dumps(tmp_head, sort_keys=True, indent=8).encode().decode('raw_unicode_escape'),     # 显示中文，只适用于json
                           'update_cookie': update_cookie1
                           }
        # 关键字列表
        public_list_all = public_para1.objects.filter(Q(module='public')|Q(module='suit')).filter(~Q(keywords__icontains='AI'))

        # csrf
        c = csrf(req)
        c.update({'id1': interface_list1['id1'],'para_dict': interface_list1['para_dict'],'para_str': interface_list1['para_str'],'head': interface_list1['head'],'mode': mode1,'body_format': body_format,'update_cookie': interface_list1['update_cookie'],'public_list_all': public_list_all,'flag_resp': flag_resp,'public_list_resp': public_list_resp})
        return render_to_response("edit_suit_interface.html",c)

#==保存接口参数
def save_edit_para_suit(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        para_info = raw_data['para_info']
        resp_info = raw_data['resp_info']

        #==body
        formated_dict = para_info[2]

        #==mode1
        mode1 = para_info[3]

        #==head1
        head1 = eval(para_info[4])
        for rec in list(head1.keys()):
            if (head1[rec] == ''):
                del head1[rec]

        #==update_cookie
        update_cookie1 = para_info[7]

        #==body_format
        body_format = para_info[8]

        id1 = para_info[0]
        if(id1 != 'new'):   #已添加的接口不需要插入assert
            interface_head = para_info[6]
            interface_name1 = interface_head.split('_')[3]

            #==update
            update_status1 = suit_interface.objects.filter(id=id1).update(interface_name=interface_name1,body=formated_dict,mode=mode1,head=head1,update_cookie=update_cookie1,body_format=body_format)
            print(update_status1,' update success!')

            # del public_para1
            public_para1.objects.filter(module_id=int(id1),module='suit').delete()   #一定要转成int才能查出来，奇葩
            print('module_id = ',id1,' delete success!')
            # insert public_para1
            if(resp_info != []):
                resp_edit_name = resp_info[0]
                resp_edit_keywords = resp_info[1]
                resp_edit_left = resp_info[2]
                resp_edit_right = resp_info[3]
                resp_edit_index = resp_info[4]

                for i in range(len(resp_edit_name)):
                    resp_info1 = public_para1(name=resp_edit_name[i],keywords=resp_edit_keywords[i],value='',left=resp_edit_left[i],right=resp_edit_right[i],index=resp_edit_index[i],module='suit',module_id=id1,type='接口返回值')
                    resp_info1.save()
                    print(resp_info1,' insert success!')

            #==回调
            current_interface = suit_interface.objects.filter(id=id1)[0]
            interface_name2 = 'suit_interface_' + str(id1) + '_' + current_interface.interface_name
            interface_list = {'id': current_interface.id,
                              'suit_id': current_interface.suit_id,
                              'suit_name': current_interface.suit_name,
                              'interface_name': interface_name2,
                              'head': current_interface.head,
                              'body': current_interface.body,
                              'mode': current_interface.mode,
                              'update_cookie': current_interface.update_cookie}
        else:   #新的接口需要插入assert
            suit_head = para_info[5]
            suit_id1 = suit_head.split('_')[0]
            suit_name1 = suit_head.split('_')[1]

            interface_head = para_info[6]
            table_name = interface_head.split('_')[0]
            id_new = interface_head.split('_')[1]
            interface_id = interface_head.split('_')[1]
            interface_name1 = interface_head.split('_')[2]
            url1 = interfaces_oeasy.objects.filter(id=interface_id)[0].url

            # assert_para
            assert_use_new1 = interfaces_oeasy.objects.filter(id=id_new)[0].assert_use_new
            assert_keywords_old1 = interfaces_oeasy.objects.filter(id=id_new)[0].assert_keywords_old
            assert_url1 = interfaces_oeasy.objects.filter(id=id_new)[0].assert_url
            assert_head1 = interfaces_oeasy.objects.filter(id=id_new)[0].assert_head
            assert_mode1 = interfaces_oeasy.objects.filter(id=id_new)[0].assert_mode
            assert_body1 = interfaces_oeasy.objects.filter(id=id_new)[0].assert_body
            assert_body_format = interfaces_oeasy.objects.filter(id=id_new)[0].assert_body_format
            assert_keywords1 = interfaces_oeasy.objects.filter(id=id_new)[0].assert_keywords
            assert_keywords_is_contain1 = interfaces_oeasy.objects.filter(id=id_new)[0].assert_keywords_is_contain

            #==insert
            para_suit_info = suit_interface(suit_id=suit_id1,suit_name=suit_name1,interface_name=interface_name1,url=url1,body_format=body_format,body=formated_dict,mode=mode1,update_cookie=update_cookie1,head=head1,assert_url=assert_url1,assert_head=assert_head1,assert_mode=assert_mode1,assert_body_format=assert_body_format,assert_body=assert_body1,assert_keywords=assert_keywords1,assert_keywords_is_contain=assert_keywords_is_contain1,assert_use_new=assert_use_new1,assert_keywords_old=assert_keywords_old1)
            para_suit_info.save()
            print(para_suit_info,' insert success!')

            # insert public_para1
            if(resp_info != []):
                resp_edit_name = resp_info[0]
                resp_edit_keywords = resp_info[1]
                resp_edit_left = resp_info[2]
                resp_edit_right = resp_info[3]
                resp_edit_index = resp_info[4]

                tmp_list = suit_interface.objects.aggregate(Max('id'))
                max_id = tmp_list['id__max']    #已经先执行了插入，所以max_id不需要加1了

                for i in range(len(resp_edit_name)):
                    resp_info1 = public_para1(name=resp_edit_name[i],keywords=resp_edit_keywords[i],value='',left=resp_edit_left[i],right=resp_edit_right[i],index=resp_edit_index[i],module='suit',module_id=max_id,type='接口返回值')
                    resp_info1.save()
                    print(resp_info1,' insert success!')

            #==查询回调参数
            max_id = suit_interface.objects.order_by('-id')[0].id
            print('max_id = ',max_id)
            current_interface = suit_interface.objects.filter(id=max_id)[0]
            interface_name2 = 'suit_interface_' + str(max_id) + '_'  + current_interface.interface_name
            interface_list = {'id': current_interface.id,
                              'suit_id': current_interface.suit_id,
                              'suit_name': current_interface.suit_name,
                              'interface_name': interface_name2,
                              'head': current_interface.head,
                              'body': current_interface.body,
                              'mode': current_interface.mode,
                              'update_cookie': current_interface.update_cookie}

        print('interface_list = ',interface_list)

        return HttpResponse(json.dumps(interface_list), content_type='application/json')

#==编辑断言
@login_required()
def show_assert_suit(req,id1):
    if req.method == "GET":
        print(id1)
        if(id1 == 'empty'):
            return HttpResponse('您未选择任何接口，请先选择接口！')
        assert_list = suit_interface.objects.filter(id=id1)
        # is_new
        is_new = assert_list[0].assert_use_new
        if(is_new == ''):
            is_new = 'false'
        # head
        head = eval(assert_list[0].assert_head)
        tmp_head = {'Accept':'','Content-Type':'','Cookie':''}
        tmp = ['Accept','Content-Type','Cookie']
        for rec in tmp:
            if(rec in list(head.keys())):
                tmp_head[rec] = head[rec]
        head1 = json.dumps(tmp_head, sort_keys=True, indent=8).encode().decode('raw_unicode_escape')
        # mode
        mode = assert_list[0].assert_mode
        if(mode == ''):
            mode = 'false'
        # is_contain
        is_contain = assert_list[0].assert_keywords_is_contain
        if(is_contain == ''):
            is_contain = 'false'
        # body
        body = assert_list[0].assert_body
        print(body)
        para_dict = json.dumps(eval(body), sort_keys=True).encode().decode('raw_unicode_escape')    # 显示中文，只适用于json
        para_str = json.dumps(eval(body), sort_keys=True, indent=8).encode().decode('raw_unicode_escape')   # 显示中文，只适用于json

        # assert_body_format
        assert_body_format = assert_list[0].assert_body_format
        if(assert_body_format == ''):
            assert_body_format = 'false'  #必须传一个值，否则传给js为空时会报错，就传false，正好匹配js的false

        # 关键字列表
        public_list = public_para1.objects.filter(Q(module='public')|Q(module='suit')).filter(~Q(keywords__icontains='AI'))

        # csrf
        c = csrf(req)
        c.update({'is_new': is_new,'assert_list': assert_list,'mode': mode,'assert_body_format': assert_body_format,'is_contain': is_contain,'head1': head1,'para_dict': para_dict,'para_str': para_str,'public_list': public_list})
        return render_to_response("assert_suit_interface.html",c)

#==保存断言
def save_assert_suit(req,id1):
    if req.method == "POST":
        raw_data = req.body
        raw_data = json.loads(raw_data)
        assert_info = raw_data['assert_info']
        print(assert_info)

        # update assert_info
        assert_head1 = eval(assert_info[2])
        for rec in list(assert_head1.keys()):
            if (assert_head1[rec] == ''):
                del assert_head1[rec]
        assert_status1 = suit_interface.objects.filter(id=id1).update(assert_url=assert_info[1],assert_head=assert_head1,assert_mode=assert_info[3],assert_body_format=assert_info[9],assert_body=assert_info[4],assert_keywords=assert_info[5],assert_keywords_is_contain=assert_info[6],assert_use_new=assert_info[7],assert_keywords_old=assert_info[8])

        print(assert_status1, ' update success!')
        return HttpResponse('update_use_status success!')
    else:
        return HttpResponse('Error')

def start_interface_suit(request):
    if request.method == "POST":
        raw_data = request.body
        raw_data = json.loads(raw_data)
        suit_id1 = raw_data['suit_id1']

        # cookie
        public_para_tmp = public_para.objects.all()[0]
        Cookie_dict = {'yypt': public_para_tmp.yypt,
                       'wypt': public_para_tmp.wypt,
                       'yhsq': public_para_tmp.yhsq,
                       'wyj': public_para_tmp.wyj,
                       'dspt': public_para_tmp.dspt,
                       'sjpt': public_para_tmp.sjpt,
                       'ggpt': public_para_tmp.ggpt,
                       'xqmc': public_para_tmp.xqmc}

        # 清空日志文件
        f_handler = open('/autotest_platform/test_out.log', 'w')
        f_handler.truncate()
        f_handler.close()

        print_log('suit_id: ',','),print_log(suit_id1)
        interfaces = suit_interface.objects.filter(suit_id=suit_id1)
        for rec in interfaces:
            url = rec.url

            #==映射head
            head = eval(rec.head)
            if(head != {} and 'Cookie' in list(head.keys())):
                for rec1 in list(Cookie_dict.keys()):
                    if(head['Cookie'] == rec1):
                        head['Cookie'] = str(Cookie_dict[rec1])
            print(head)
            #==映射body
            body = eval(rec.body)
            for rec1 in list(body.keys()):
                if(body[rec1] == u'xqmc'):
                    body[rec1] = str(Cookie_dict['xqmc'])
                elif('xqmc' in body[rec1] and (body[rec1] != u'xqmc') and ('select' not in body[rec1])):
                    body[rec1] = body[rec1].replace('xqmc',str(Cookie_dict['xqmc']))
                elif('xqid' in body[rec1]):
                    sql = 'select * from basedata.t_base_unit where `name`="'+str(Cookie_dict['xqmc'])+'"'
                    cursor = connection.cursor()
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    xqid = data[0][0]
                    body[rec1] = body[rec1].replace('xqid',xqid)
                elif(body[rec1] == u'yhsq'):
                    body[rec1] = str(Cookie_dict['yhsq'])
                elif(body[rec1] == u'wyj'):
                    body[rec1] = str(Cookie_dict['wyj'])
                elif('select' in body[rec1]):
                    sql = body[rec1]
                    if('xqmc' in body[rec1]):       #替换xqid
                        sql = body[rec1].replace('xqmc',str(Cookie_dict['xqmc']))
                    cursor = connection.cursor()
                    print(sql)
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    print(u'查询的id为： ',data[0][0])
                    body[rec1] = data[0][0]
            print(body)

            mode = rec.mode
            body_format = 'NOT_JSON'
            #==测试开始
            if(interface_test_start(url,body,head,mode,body_format,True) == 0):     #False，不打印日志；True，打印日志
                time.sleep(1)
                continue
            else:
                break
        #==日志
        File = '/autotest_platform/test_out.log'
        File1 = open(File,'r')
        test_log = File1.readlines()
        #==去掉test_log中的'<>'，否则textarea中无法看到输入结果
        test_log = str(test_log)
        test_log = test_log.replace('<','[').replace('>',"]")
        test_log = eval(test_log)
        return HttpResponse(test_log)


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

            print_log('cur_id: ',','),print_log(cur_id)
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
            response,cookie = interface_test_start(url,body,head,mode,body_format,False)     #False，不打印日志；True，打印日志

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
                    api_test_result1(1, cur_id)
                    print('testresult=测试通过')
                else:
                    api_test_result(cur_id, response, 0)
                    api_test_result1(0, cur_id)
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
                    api_test_result1(1, cur_id)
                    print('testresult=测试通过')
                else:
                    api_test_result(cur_id, response, 0)
                    api_test_result1(0, cur_id)
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


   #写入测试结果-<!-- author:zh  date:2018-08-02  -->
def api_test_result(suit_id,response,result):
    result = result
    response = response#.encode('utf-8')
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO `app_interface_suit_result` (`suit_id`,`suit_interface_id`, `response`, `result`,`date_time`)  VALUES ('%s','1','%s','%s','%s');"%(suit_id,response,result,now)
    print ('api autotest result is '+str(result))
    cursor = connection.cursor()
    cursor.execute(sql)
    cursor.close()

    # 写入测试结果-<!-- author:zh  date:2018-08-02  -->
def api_test_result1(result,id):
    result = result
    sql = "UPDATE app_interface_suit_interface set app_interface_suit_interface.interface_testresult=%s where app_interface_suit_interface.id=%s;"
    param = (result,id)
    print ('api autotest result1 is ' + str(result))
    cursor = connection.cursor()
    cursor.execute(sql,param)
    cursor.close()


#测试报告-<!-- author:zh  date:2018-08-06  -->
def apitestreport(request):
    apisuit_list = suit_interface.objects.all()      #获取测试套测试用例\
    suit_list = suit.objects.all()
    apisuit_count = suit_interface.objects.all().count()  #
    cursor = connection.cursor()
    pass_sql = "select count(id) from app_interface_suit_interface where app_interface_suit_interface.interface_testresult=1"
    aa=cursor.execute(pass_sql)
    pass_count = [row[0] for row in cursor.fetchmany(aa)][0]
    fail_sql = "select count(id) from app_interface_suit_interface where app_interface_suit_interface.interface_testresult=0"
    bb=cursor.execute(fail_sql)
    fail_count = [row[0] for row in cursor.fetchmany(bb)][0]
    ng_count= apisuit_count-pass_count-fail_count
    suit_result_list = suit_result.objects.all().order_by('-date_time')
    cursor.close()
    print(apisuit_list,'!!!!!')
    return render_to_response("interface_report.html",{'apisuit_lists': apisuit_list,"apisuit_counts": apisuit_count,'suit_lists': suit_list,'pass_counts': pass_count,'fail_counts': fail_count,'ng_counts': ng_count,'suit_result_lists':suit_result_list})
#    return render_to_response("interface_report.html",{'apisuit_lists': apisuit_list,"apisuit_counts": apisuit_count,'suit_lists': suit_list,'suit_result_lists':suit_result_list})

#搜索测试结果
def reportsearch(request):
  #  search_datetime = request.GET.get("date_time", "")
    search_interfaceid = request.GET.get("suit_id","")
    suit_result_list = suit_result.objects.filter(suit_id__icontains=search_interfaceid)
   # suit_result_list = suit_result.objects.filter(date_time__icontains=search_datetime)
    return render(request, 'interface_report.html', {"suit_result_lists": suit_result_list})

#周期任务
def settask(request):
    return render_to_response("periodic_task.html")

def task_apis(request):
    hello_world()
    return HttpResponse("已运行")

#def task_interface_suit1(request):
#    start_interface_suit1(request)
#    return HttpResponse("已运行")

# 任务计划
def periodic_task(request):
   # username = request.session.get('user', '')
    task_list = PeriodicTask.objects.all()
    periodic_list = IntervalSchedule.objects.all()  # 周期任务 （如：每隔1小时执行1次）
    crontab_list = CrontabSchedule.objects.all()    # 定时任务 （如：某年月日的某时，每天的某时）
    cursor = connection.cursor()
    print(task_list)
    cursor.close()
    return render(request, "periodic_task.html", {"tasks": task_list, "periodics": periodic_list,"crontabs": crontab_list })
'''
# 搜索功能
def tasksearch(request):
   # username = request.session.get('user', '') # 读取浏览器登录session
    search_name = request.GET.get("task", "")
    task_list = PeriodicTask.objects.filter(task__icontains=search_name)
    periodic_list = IntervalSchedule.objects.all()  # 周期任务 （如：每隔1小时执行1次）
    crontab_list = CrontabSchedule.objects.all()    # 定时任务 （如：某年月日的某时，每天的某时）
    return render(request,'periodic_task.html', {"tasks":task_list,"periodics": periodic_list,"crontabs": crontab_list })
'''



#测试报告发送到邮箱
def testreport_to_email(self):
    yag = yagmail.SMTP(user="zouhui@0easy.com", password="Test123456", host="smtp.exmail.qq.com")
    contents = ['测试报告邮件:','接口自动化测试结果 ','通过']

    to1 = '7980068@qq.com'
    to2 = '357542696@qq.com'
    cc_mail = ['lizhenliang@xxx.com']
    subject = '接口自动化测试报告邮件'
    body = '测试详情如下：'
    html = '<a href="http://192.168.2.172/apitestreport/">Click me!</a>'

    yag.send(to=to1,subject=subject,contents=[body,html])
    return render_to_response('interface_report.html')