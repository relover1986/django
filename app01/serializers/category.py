from rest_framework import serializers
from app01.models import CategoryContent


class CategoryContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryContent
        fields = '__all__'
