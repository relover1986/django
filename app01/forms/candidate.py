from django import forms
from django.core.exceptions import ValidationError
from app01 import models
import arrow


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = models.Candidate
        fields = '__all__'
        exclude = ['created_at', 'resume_file']  # 自动生成的字段不需要在表单中显示
        widgets = {
            'birthday': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'photo': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为所有字段添加bootstrap样式
        for field_name, field in self.fields.items():
            if field_name not in ['photo', 'birthday']:  # 已经单独设置样式的字段跳过
                field.widget.attrs.update({'class': 'form-control'})
            # 设置日期字段初始值
            if field_name == 'birthday':
                field.initial = arrow.now().format('YYYY-MM-DD')

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name.strip()) < 2:
            raise ValidationError("姓名至少需要2个字符")
        return name.strip()
