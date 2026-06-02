from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from app01 import models
from app01.jiami import md5
import django_filters


class StaffFilter(django_filters.FilterSet):
    class Meta:
        model = models.Admin
        fields = ['username', 'role', 'department']  # 可筛选的字段


class Staff(forms.ModelForm):
    username = forms.CharField(label='姓名')
    department = forms.CharField(label='部门')
    # 新增照片上传字段
    avatar = forms.ImageField(
        label="管理员头像",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',  # 保留原有样式
                'accept': 'image/*'       # 新增类型限制
            }
        )
    )

    class Meta:
        model = models.Admin
        fields = "__all__"  # 以列表的形式写入字段
        exclude = ["id"]

    password = forms.CharField(required=True, widget=forms.PasswordInput(render_value=True), label="密码")
    password_ = forms.CharField(required=True, widget=forms.PasswordInput(render_value=True), label="再次输入")

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return md5(pwd)

    def clean_password_(self):
        pwd = self.cleaned_data.get('password')
        pwd_ = self.cleaned_data.get('password_')
        print(md5(pwd))
        if pwd != md5(pwd_):
            raise ValidationError("输入不一错误")
        return pwd_

    def clean(self):
        cleaned_data = super().clean()
        for field_name, field in self.fields.items():
            # 跳过允许为空的字段
            if field.required and not cleaned_data.get(field_name):
                self.add_error(field_name, "该字段不能为空")
        return cleaned_data

    # 新增文件大小验证（可选）
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if isinstance(avatar, InMemoryUploadedFile):
            if avatar.size > 20 * 1024 * 1024:
                raise ValidationError("头像文件大小不能超过20MB")
            # 新增返回验证通过的文件
            return avatar
        return avatar  # 修改这里保持已有文件不变
