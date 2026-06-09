"""Models: staff domain"""
import re
import os
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class Staff(models.Model):
    """人员基础信息主表"""
    name = models.CharField(max_length=32, verbose_name="姓名", blank=True)
    id_number = models.CharField(max_length=18, verbose_name="身份证号", unique=True, blank=True)
    phone = models.CharField(max_length=11, verbose_name="手机号")
    password = models.CharField(max_length=128, verbose_name="密码", default='888')
    department = models.CharField(max_length=64, verbose_name="部门", blank=True)
    status = models.CharField(
        max_length=16, verbose_name="状态", default="在职",
        choices=[("在职", "在职"), ("离职", "离职"), ("挂靠", "挂靠")]
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "人员信息"
        verbose_name_plural = "人员信息"
        db_table = "app01_staff"

    def __str__(self):
        return self.name


class CertType(models.Model):
    """证件类型字典表"""
    name = models.CharField(max_length=64, verbose_name="证件名称", unique=True)
    remark = models.CharField(max_length=128, verbose_name="备注", blank=True)
    sort = models.IntegerField(verbose_name="排序", default=0)

    class Meta:
        verbose_name = "证件类型"
        verbose_name_plural = "证件类型"
        db_table = "app01_cert_type"

    def __str__(self):
        return self.name


class StaffCert(models.Model):
    """人员证件明细表"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, verbose_name="人员")
    cert_type = models.ForeignKey(CertType, on_delete=models.CASCADE, verbose_name="证件类型")
    cert_number = models.CharField(max_length=64, verbose_name="证件编号", blank=True)
    issue_date = models.DateField(verbose_name="发证日期", null=True, blank=True)
    expire_date = models.DateField(verbose_name="到期日期", null=True, blank=True)
    status = models.CharField(
        max_length=16, verbose_name="状态", default="有效",
        choices=[("有效", "有效"), ("过期", "过期"), ("作废", "作废")]
    )
    remark = models.TextField(verbose_name="备注", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "人员证件"
        verbose_name_plural = "人员证件"
        db_table = "app01_staff_cert"

    def __str__(self):
        return f"{self.staff.name} - {self.cert_type.name}"


class StaffCertFile(models.Model):
    """证件附件/图片表"""
    cert = models.ForeignKey(StaffCert, on_delete=models.CASCADE, verbose_name="证件")
    file = models.ImageField(upload_to="certs/%Y/%m/", verbose_name="文件")
    file_type = models.CharField(
        max_length=16, verbose_name="文件类型",
        choices=[("正面", "正面"), ("反面", "反面"), ("扫描件", "扫描件"), ("其他", "其他")],
        default="其他"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "证件附件"
        verbose_name_plural = "证件附件"
        db_table = "app01_staff_cert_file"

    def __str__(self):
        return f"{self.cert.staff.name} - {self.cert.cert_type.name} - {self.file_type}"


