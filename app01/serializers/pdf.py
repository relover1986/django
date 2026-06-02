from rest_framework import serializers
from app01.models import UploadedPDF


class UploadedPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedPDF
        fields = '__all__'
