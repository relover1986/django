from django.core.validators import RegexValidator
from django.db import models


class InfoSubmission(models.Model):
    """公开信息提交"""
    front_photo = models.ImageField(upload_to='info_submissions/', null=True, blank=True, verbose_name='证件人像页')
    back_photo = models.ImageField(upload_to='info_submissions/', null=True, blank=True, verbose_name='证件国徽页')
    one_inch_photo = models.ImageField(upload_to='info_submissions/', null=True, blank=True, verbose_name='一寸照片')
    phone = models.CharField(max_length=11, validators=[RegexValidator(r'^1\d{10}$')], verbose_name='手机号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')

    # Step 1/3 — 模型加可选字段
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name='姓名')
    id_number = models.CharField(max_length=18, null=True, blank=True, verbose_name='身份证号')
    address = models.TextField(null=True, blank=True, verbose_name='地址')
    remark = models.TextField(null=True, blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '信息收集'
        verbose_name_plural = '信息收集记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.phone} - {self.name or "未填写姓名"}'
