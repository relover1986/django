"""Models: hr domain"""
import re
import os
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class Candidate(models.Model):
    GENDER_CHOICES = [('男', '男性'), ('女', '女性')]
    MARITAL_CHOICES = [('未婚', '未婚'), ('已婚', '已婚')]
    LICENSE_CHOICES = [('有', '有驾照'), ('无', '无驾照')]

    name = models.CharField(max_length=20, verbose_name='姓名')
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, verbose_name='性别')

    mobile = models.CharField(
        max_length=11,
        verbose_name='手机',
        default='',  # 修复: 从default=30改为空字符串
        blank=False
    )

    age= models.IntegerField(
        verbose_name='年龄',
        null=True,
        blank=True,
        default=30,
        validators=[MinValueValidator(18), MaxValueValidator(65)]  # 添加数值范围验证
    )

    marital_status = models.CharField(max_length=2, choices=MARITAL_CHOICES, verbose_name='婚姻状况')
    education = models.CharField(max_length=50, verbose_name='学历+专业')
    has_driver_license = models.CharField(max_length=2, choices=LICENSE_CHOICES, verbose_name='驾照')
    special_skills = models.TextField(verbose_name='特长')
    work_experience = models.TextField(verbose_name='工作经历')
    current_address = models.CharField(verbose_name='现住所', max_length=10, blank=True, default='')
    position = models.CharField(max_length=20, verbose_name='应聘岗位', default='')
    expected_salary = models.CharField(max_length=20, verbose_name='期望薪资')
    photo = models.ImageField(
        upload_to='candidate_photos/',
        verbose_name='一寸照',  # 修改此处的verbose_name
        blank=True,
        null=True
    )
    # 新增简历文件字段
    resume_file = models.FileField(
        upload_to='resumes/',
        verbose_name='简历文件',
        blank=True,default='',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '求职者档案'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_gender_display()}"

class ContractLabor(models.Model):
    name = models.CharField(max_length=4, verbose_name='姓名')
    id_number = models.CharField(max_length=18, verbose_name='身份证号')

    contract_file = models.FileField(
        upload_to='contractlabor/',
        verbose_name='劳动合同'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

