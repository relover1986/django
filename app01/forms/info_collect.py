from django import forms
from django.core.validators import RegexValidator

class InfoCollectForm(forms.Form):
    front_photo = forms.ImageField(required=False, label='证件人像页（选填）')
    back_photo = forms.ImageField(required=False, label='证件国徽页（选填）')
    one_inch_photo = forms.ImageField(required=False, label='一寸照片（选填）')
    phone = forms.CharField(
        required=True, max_length=11, label='手机号码',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入11位手机号'}),
        validators=[RegexValidator(regex=r'^1\d{10}$')]
    )
