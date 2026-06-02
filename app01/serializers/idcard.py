from rest_framework import serializers
from app01.models import IDCard


class IDCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = IDCard
        fields = '__all__'
