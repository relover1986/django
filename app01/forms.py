from django import forms
from app01 import models


class StaffForm(forms.ModelForm):
    class Meta:
        model = models.Staff
        fields = ["name", "id_number", "phone", "department", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # choices 字段（如 status）用 form-select，其余用 form-control
            css = 'form-select' if hasattr(field, 'choices') and field.choices else 'form-control'
            field.widget.attrs.update({'class': css})


class CertTypeForm(forms.ModelForm):
    class Meta:
        model = models.CertType
        fields = ['name', 'remark']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class StaffCertForm(forms.ModelForm):
    class Meta:
        model = models.StaffCert
        fields = ['cert_type', 'cert_number', 'issue_date', 'expire_date', 'status', 'remark']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field, forms.DateField):
                # 日期字段 → DateInput type=date
                field.widget = forms.DateInput(attrs={
                    'type': 'date', 'class': 'form-control'
                })
            elif hasattr(field, 'choices') and field.choices:
                # FK / choices 下拉 → form-select
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class StaffCertFileForm(forms.ModelForm):
    class Meta:
        model = models.StaffCertFile
        fields = ['file', 'file_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(attrs={
                    'type': 'date', 'class': 'form-control'
                })
            elif hasattr(field, 'choices') and field.choices:
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class WorkerForm(forms.ModelForm):
    class Meta:
        model = models.Worker
        fields = ["name", "job_type", "photo"]
        labels = {"name": "姓名", "job_type": "工种"}
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "请输入姓名", "form": "manual-form"}),
            "job_type": forms.TextInput(attrs={"class": "form-control", "placeholder": "选择或输入工种", "list": "job-type-list", "form": "manual-form"}),
            "photo": forms.FileInput(attrs={"class": "d-none", "accept": "image/*", "id": "manual-photo-input"}),
        }

    def clean_job_type(self):
        return self.cleaned_data["job_type"]  # 允许手动输入自定义工种


class ExcelUploadForm(forms.Form):
    excel = forms.FileField(label="上传Excel", widget=forms.FileInput(attrs={
        "class": "form-control",
        "accept": ".xlsx,.xls",
    }))


class PhotoForm(forms.ModelForm):
    class Meta:
        model = models.Worker
        fields = ["photo"]
        labels = {"photo": ""}
        widgets = {
            "photo": forms.FileInput(attrs={"class": "photo-file-input d-none", "accept": "image/*"}),
        }
