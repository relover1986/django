from django import forms
from app01 import models
import arrow


class Ti(forms.ModelForm):
    class Meta:
        model = models.Tihao
        fields = []  # 以列表的形式写入字段

    ti = [v['题号'] for i, v in enumerate(models.Tihao.objects.values('题号'))]
    id = locals()
    choice = [(v, v) for i, v in enumerate(list('ABCDE对错'))]

    for i in ti:
        id[str(i)] = forms.MultipleChoiceField(choices=choice, required=False, label=str(i), widget=forms.CheckboxSelectMultiple(),)  # widget=forms.CheckboxSelectMultiple,

    date = forms.DateField(required=True, initial=arrow.now().shift(days=0).format('YYYY-MM-DD'),
                           error_messages={'required': '由于计划不能为空'},
                           widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}), label="日期")


class Ti1(forms.ModelForm):
    class Meta:
        model = models.Tihao
        fields = []  # 以列表的形式写入字段

    ti = [v['题号'] for v in models.Tihao.objects.values('题号') if '多选' not in str(v['题号'])]
    id = locals()
    choice = [(v, v) for i, v in enumerate(list('ABCDE对错'))]

    for i in ti:
        id[str(i)] = forms.MultipleChoiceField(choices=choice, required=False, label=str(i), widget=forms.CheckboxSelectMultiple(),)  # widget=forms.CheckboxSelectMultiple,

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态设置日期初始值
        self.fields['date'].initial = arrow.now().format('YYYY-MM-DD')

    date = forms.DateField(
        required=True,
        error_messages={'required': '由于计划不能为空'},
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date'}
        ),
        label="日期"
    )
