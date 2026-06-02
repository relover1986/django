from rest_framework import serializers
from app01.models import UploadedTu


class UploadedTuSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedTu
        fields = '__all__'
