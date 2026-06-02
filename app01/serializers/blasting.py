from rest_framework import serializers
from app01.models import BlastingCertificate


class BlastingCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlastingCertificate
        fields = '__all__'
