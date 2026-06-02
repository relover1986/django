from rest_framework import serializers
from app01.models import ExplosiveInventoryItem


class ExplosiveInventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExplosiveInventoryItem
        fields = '__all__'
