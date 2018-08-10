from __future__ import unicode_literals
from django.db import models

# Create your models here.
class public_para(models.Model):
    yypt = models.TextField("运营平台",null=True)
    wypt = models.TextField("物业平台",null=True)
    yhsq = models.TextField("一号社区",null=True)
    wyj = models.TextField("物业+",null=True)
    dspt = models.TextField("电商平台",null=True)
    sjpt = models.TextField("商家平台",null=True)
    ggpt = models.TextField("广告平台",null=True)
    xqmc = models.CharField("小区名称",max_length=255,null=True)

class public_para1(models.Model):
    name = models.CharField("名称",max_length=100,null=True)
    keywords = models.CharField("关键字",max_length=100,null=True)
    value = models.TextField("值",null=True)
    left = models.TextField("左边界",null=True)
    right = models.TextField("右边界",null=True)
    index = models.CharField("索引",max_length=20,null=True)
    module = models.CharField("模块",max_length=20,null=True)
    module_id = models.CharField("模块id",max_length=20,null=True)
    type = models.CharField("类型",max_length=20,null=True)

class interfaces_oeasy(models.Model):
    name = models.CharField("接口名称",max_length=100,null=True)
    url = models.TextField("url",null=True)
    head = models.TextField("head",null=True)
    body_format = models.CharField("请求参数格式",max_length=20,null=True)
    body = models.TextField("请求参数",null=True)
    mode = models.CharField("请求方式",max_length=30,null=True)
    charger = models.CharField("负责人",max_length=20,null=True)
    order = models.IntegerField("排序",null=True)
    module = models.CharField("模块",max_length=30,null=True)
    update_cookie = models.CharField("是否更新cookie",max_length=10,null=True)
    assert_use_new = models.CharField("是否使用新接口作为断言",max_length=10,null=True)
    assert_keywords_old = models.TextField("断言的关键字",null=True)
    assert_url = models.TextField("断言的url",null=True)
    assert_head = models.TextField("断言的head",null=True)
    assert_mode = models.CharField("断言的请求方式",max_length=10,null=True)
    assert_body_format = models.CharField("断言的请求参数格式",max_length=20,null=True)
    assert_body = models.TextField("断言的请求参数",null=True)
    assert_keywords = models.TextField("断言的关键字",null=True)
    assert_keywords_is_contain = models.CharField("是否包含",max_length=10,null=True)
    # AI
    assert_use_new_AI = models.CharField("是否使用新接口作为AI断言",max_length=10,null=True)
    assert_url_AI = models.TextField("AI断言的url",null=True)
    assert_head_AI = models.TextField("AI断言的head",null=True)
    assert_mode_AI = models.CharField("AI断言的请求方式",max_length=10,null=True)
    assert_body_format_AI = models.CharField("AI断言的请求参数格式",max_length=20,null=True)
    assert_body_AI = models.TextField("AI断言的请求参数",null=True)
    assert_keywords_is_contain_AI = models.CharField("是否包含",max_length=10,null=True)
    assert_keywords_new_AI = models.TextField("AI断言的关键字",null=True)
    assert_keywords_old_AI = models.TextField("AI断言的关键字",null=True)

    # def __str__("",self):    #不要加这个东西，会导致save写入数据库时报错TypeError: __str__ returned non-string ("",type tuple)
    #     return self.name    #在admin中显示name

class suit(models.Model):
    suit_name = models.CharField("测试套名称",max_length=100,null=True)
    interface_name = models.TextField("接口名称",null=True)
    interface_name_display = models.TextField("用于展示的接口名称",null=True)
    charger = models.CharField("负责人",max_length=20,null=True)
    orders = models.IntegerField("排序",null=True)

class suit_interface(models.Model):
    suit_id = models.IntegerField("测试套id",null=True)
    suit_name = models.CharField("测试套名称",max_length=100,null=True)
    interface_name = models.CharField("接口名称",max_length=100,null=True)
    url = models.TextField("url",null=True)
    head = models.TextField("head",null=True)
    body_format = models.CharField("请求参数格式",max_length=20,null=True)
    body = models.TextField("请求参数",null=True)
    mode = models.CharField("请求方式",max_length=10,null=True)
    update_cookie = models.CharField("是否更新cookie",max_length=10,null=True)
    assert_use_new = models.CharField("是否使用新接口作为断言",max_length=10,null=True)
    assert_keywords_old = models.TextField("断言的关键字",null=True)
    assert_url = models.TextField("断言的url",null=True)
    assert_head = models.TextField("断言的head",null=True)
    assert_mode = models.CharField("断言的请求方式",max_length=10,null=True)
    assert_body_format = models.CharField("断言的请求参数格式",max_length=20,null=True)
    assert_body = models.TextField("断言的请求参数",null=True)
    assert_keywords = models.TextField("断言的关键字",null=True)
    assert_keywords_is_contain = models.CharField("是否包含",max_length=10,null=True)
    interface_testresult = models.IntegerField(null=True)

class suit_result(models.Model):
    suit_id = models.IntegerField("测试套id",null=True)
    suit_interface_id = models.IntegerField("接口id",null=True)
    response = models.TextField("响应信息",null=True)
    result = models.CharField("测试结果",max_length=20,null=True)
    date_time = models.CharField("时间",max_length=20,null=True)