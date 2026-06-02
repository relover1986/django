from django import forms
from app01 import models
import arrow


class ExplosiveInventoryItemForm(forms.ModelForm):
    class Meta:
        model = models.ExplosiveInventoryItem
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 定义一个列表，包含需要排除的字段名
        exclude_fields = [
            'inventory_order_number',
            'emulsion_explosive_32mm', 'powdery_explosive_box_2', 'sticky_explosive', 'electronic_detonator_5m', 'electronic_detonator_15m',
            'detonator_code',
            'inventory_status',
            'explosive_quantity_90mm',
            'explosive_quantity_32mm',
            'detonating_device_quantity',
            'detonating_cord_length',
            'date'
        ]

        for field_name, field in self.fields.items():
            if field_name not in exclude_fields:
                # 使用自定义的 ContentChoiceField 替换需要显示 content 字段的字段
                choice = [(v['content'], v['content']) for i, v in enumerate(models.CategoryContent.objects.values('category', 'content')) if v['category'] == field_name]  # field_name

                choice = list(set(choice))
                choice.sort()

                self.fields[field_name] = forms.ChoiceField(choices=choice)

                # 设置字段的标签为模型字段的 verbose_name
                self.fields[field_name].label = self.Meta.model._meta.get_field(field_name).verbose_name
                self.fields['date'].initial = arrow.now().format('YYYY-MM-DD')
