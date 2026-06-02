from rest_framework import serializers
from app01.models import LoginRecords


class LoginRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginRecords
        fields = '__all__'
