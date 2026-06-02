from rest_framework import serializers
from app01.models import ContractLabor


class ContractLaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractLabor
        fields = '__all__'
