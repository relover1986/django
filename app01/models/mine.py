"""Models: mine domain"""
import re
import os
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError




def photo_upload_path(instance, filename):
    "用姓名+入井证命名"
    name = re.sub(r"[^\w\u4e00-\u9fff-]", "", instance.name)
    return f"photos/{name}_入井证.jpg"


class Worker(models.Model):
    JOB_TYPE_CHOICES = [
        ("爆破员", "爆破员"),
        ("安全员", "安全员"),
        ("工程师", "工程师"),
    ]
    name = models.CharField("姓名", max_length=50)
    job_type = models.CharField("工种", max_length=50, choices=JOB_TYPE_CHOICES, default="爆破员")
    photo = models.ImageField("一寸照片", upload_to=photo_upload_path, blank=True, null=True)
    department = models.CharField("所属部门", max_length=64, default='', blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "入井人员"
        verbose_name_plural = "入井人员"

    def __str__(self):
        return f"{self.name} - {self.job_type}"

class JobType(models.Model):
    """工种模型"""
    name = models.CharField("工种", max_length=50, unique=True)
    responsibilities = models.TextField("岗位职责", blank=True, default="")

    class Meta:
        verbose_name = "工种"
        verbose_name_plural = "工种"
        ordering = ["name"]

    def __str__(self):
        return self.name

class UploadedZhaopian(models.Model):
    # 定义一个字段来存储上传的PDF文件
    name = models.CharField(max_length=10, blank=True, null=True, verbose_name='姓名')  # 新增姓名字段
    photo = models.FileField(upload_to='photo/', verbose_name='原始照片')  # 添加verbose_name

    rotated_photo = models.ImageField(
        upload_to='rotated/',
        default='',
        verbose_name='排版'  # 已存在保持不动
    )

    blue_background = models.ImageField(
        upload_to='blue_background/',
        verbose_name='蓝底',  # 修改此处
        blank=True,
        null=True,
        default=''
    )
    red_background = models.ImageField(
        upload_to='red_background/',
        verbose_name='红底',  # 修改此处
        blank=True,
        null=True,
        default=''
    )
    white_background = models.ImageField(
        upload_to='white_background/',
        verbose_name='白底',  # 修改此处
        blank=True,
        null=True,
        default=''
    )

    white_bg_single = models.ImageField(
        upload_to='white_bg_single/',
        verbose_name='白底一寸照',
        blank=True,
        null=True,
        default=''
    )

    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')  # 添加verbose_name

class IDCard(models.Model):
    name = models.CharField(max_length=100, verbose_name='姓名')
    id_number = models.CharField(max_length=18, verbose_name='身份证号')
    front_image = models.ImageField(
        upload_to='ids/',
        verbose_name='人像面照片'
    )
    back_image = models.ImageField(
        upload_to='ids/',
        verbose_name='国徽面照片'
    )
    combined_image = models.ImageField(
        upload_to='combined/',
        verbose_name='双面合成图',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

