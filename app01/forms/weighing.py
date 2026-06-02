from django import forms
from app01 import models


class WeighingRecordForm(forms.ModelForm):
    class Meta:
        model = models.WeighingRecord
        exclude = ['created_at']  # 自动生成的时间字段无需填写
        labels = {
            'weight_number': '磅单号',
            'truck_driver': '大车司机',
            'forklift_driver': '铲车司机',
            'net_weight': '矿石净重',
            'weight_photo': '称重单照片'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为所有字段添加 Bootstrap 样式
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # 特殊处理图片字段
        self.fields['weight_photo'].widget = forms.ClearableFileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*'
        })
