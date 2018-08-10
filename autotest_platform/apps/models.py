from __future__ import unicode_literals
from django.db import models

# Create your models here.
class sn(models.Model):
    sn = models.TextField(null=True)

class user_info(models.Model):
    user = models.CharField(max_length=100,null=True)
    password = models.CharField(max_length=100,null=True)
    pay_password = models.CharField(max_length=100,null=True)
    name = models.CharField(max_length=100,null=True)
    sex = models.CharField(max_length=10,null=True)
    birth = models.CharField(max_length=100,null=True)
    phone = models.CharField(max_length=20,null=True)
    email = models.CharField(max_length=100,null=True)
    id_card = models.CharField(max_length=50,null=True)
    qq = models.CharField(max_length=20,null=True)
    weixin = models.CharField(max_length=20,null=True)
    pre_name = models.CharField(max_length=100,null=True)
    pre_id_card = models.CharField(max_length=50,null=True)