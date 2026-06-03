"""Models: auth domain"""
import re
import os
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class User(models.Model):
    """用户表"""
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
class Admin(models.Model):
    # id = models.BigAutoField(primary_key=True)
    ident = models.CharField(max_length=32)
    username = models.CharField(max_length=32)
    role = models.CharField(max_length=32, verbose_name='身份')  # 修改字段名称
    password = models.CharField(max_length=64)
    department = models.CharField(max_length=32, default='')

    avatar = models.ImageField(upload_to='avatars/admin/',  # 存储路径
                            null=True,
                            blank=True,
                            default='avatars/admin/default_avatar.png')  # 默认路径

class LoginRecords(models.Model):

    ip = models.CharField(verbose_name='ip',max_length=32)
    time = models.DateTimeField(blank=False, null=False,auto_now_add=True)
    ident= models.CharField(max_length=32, default='')
    name = models.CharField(verbose_name='用户名',max_length=32)
    job = models.CharField(verbose_name='职位',max_length=32)
    type = models.CharField(verbose_name='登入登出',max_length=32)

    # class Meta:
    #     verbose_name = '登录记录'
    #     verbose_name_plural = verbose_name
    #     ordering = ['-time']
    # def __str__(self):
    #     return self.name

