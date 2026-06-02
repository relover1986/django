from django import forms
from app01 import models


class CategoryContentForm(forms.ModelForm):
    class Meta:
        model = models.CategoryContent
        fields = '__all__'
