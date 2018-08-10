# -*- coding: utf-8 -*-
from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from apps.get_captcha import gene_code
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.core.cache import cache
from config import *
import json,random
from django.template.context_processors import csrf
from djcelery.schedulers import DatabaseScheduler

@login_required()
def index(request):
    cur_user = request.user.username
    print(cur_user)
    print(request.META['REMOTE_ADDR'])   #获取客户端ip
    c = csrf(request)
    c.update({'cur_user':cur_user})
    return render(request, 'index.html',c)

#登陆
def login_captcha_img(req):
    if req.method=='POST':
        username= req.POST.get('username', '')
        password = req.POST.get('password', '')
        captcha = req.POST.get('captcha', '')
        # 获取验证码
        ip = req.META['REMOTE_ADDR']   #获取客户端ip
        ip = str(ip).replace('.','_')
        var = "captcha_"+ip
        print(cache.get(var))
        if(cache.get(var) != None):
            if (captcha.lower() == cache.get(var).lower()):
                print(username, password)
                user = auth.authenticate(username=username,password=password)
                try:
                    auth.login(req, user)
                    return HttpResponseRedirect("/index/")
                except Exception:
                    return HttpResponse("密码错误")
            else:
                return HttpResponseRedirect("/login/")  #验证码错误就刷新页面，因为jq validate equal无法区分大小写
        else:
            return HttpResponseRedirect("/login/")  #验证码过期就刷新页面
    captcha = gene_code('/static/verify_code_imgs/','verify_code')
    # 验证码写入缓存
    ip = req.META['REMOTE_ADDR']   #获取客户端ip
    ip = str(ip).replace('.','_')
    var = "captcha_"+ip
    cache.set(var, captcha, timeout=300)
    print(var,cache.get(var))
    # csrf
    c = csrf(req)
    c.update({'captcha': captcha})
    return render_to_response("login_both.html",c)

#更换验证码
def update_captcha(request,num):
    captcha = gene_code('/static/verify_code_imgs/','verify_code')
    captcha_info = {'num': num,
                    'captcha': captcha}
    # 验证码写入缓存
    ip = request.META['REMOTE_ADDR']   #获取客户端ip
    ip = str(ip).replace('.','_')
    var = "captcha_"+ip
    cache.set(var, captcha, timeout=300)
    print(var,cache.get(var))
    return HttpResponse(json.dumps(captcha_info), content_type='application/json')

#登陆，登录验证码不需要有5分钟限制
def login(req):
    if req.method=='POST':
        username= req.POST.get('username', '')
        password = req.POST.get('password', '')
        captcha = req.POST.get('captcha', '')
        captcha1 = req.POST.get('captcha1', '')
        print(captcha,captcha1)
        if (captcha.lower() == captcha1.lower()):
            print(username, password)
            user = auth.authenticate(username=username,password=password)
            try:
                auth.login(req, user)
                return HttpResponseRedirect("/index/")
            except Exception:
                return HttpResponse("密码错误")
        else:
            return HttpResponseRedirect("/login/")  #验证码错误就刷新页面，因为jq validate equal无法区分大小写
    # 给一个初始验证码，因为js的onload方法在谷歌浏览器无效
    # code = str(random.randint(0,999999)).zfill(6)
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(4):
        sa.append(random.choice(seed))
    code = ''.join(sa)
    # csrf
    c = csrf(req)
    c.update({'code': code})
    return render_to_response("login_both.html",c)

#注销
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/login/")
