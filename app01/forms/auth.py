from django import forms
from app01.jiami import md5


class Login(forms.Form):
    ident = forms.CharField(label='账号', widget=forms.TextInput)

    password = forms.CharField(
        label='密码',
        error_messages={'required': '密码不能为空'},
        widget=forms.PasswordInput)

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return md5(pwd)

    def __init__(self, *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {'class': 'form-control'}
