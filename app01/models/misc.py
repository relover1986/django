"""Models: misc domain"""
import re
import os
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class UploadedPDF(models.Model):
    # 定义一个字段来存储上传的PDF文件
    model_name = models.CharField(max_length=100, default='')
    pdf_file = models.FileField(upload_to='pdfs/')

class UploadedTu(models.Model):
    # 定义一个字段来存储上传的PDF文件
    model_name = models.CharField(max_length=100, default='')
    pdf_file = models.FileField(upload_to='tu/')

class PushSubscription(models.Model):
    """Web push subscription for PWA notifications"""
    endpoint = models.CharField(max_length=255, unique=True, verbose_name='推送端点')
    p256dh = models.TextField(blank=True, default='', verbose_name='p256dh密钥')
    auth = models.TextField(blank=True, default='', verbose_name='auth密钥')
    user_agent = models.TextField(blank=True, default='', verbose_name='用户代理')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '推送订阅'
        verbose_name_plural = '推送订阅'
        ordering = ['-created_at']

    def __str__(self):
        return f'Push sub {self.id} ({self.created_at.strftime("%Y-%m-%d")})'


