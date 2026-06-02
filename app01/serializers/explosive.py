from rest_framework import serializers
from app01.models import ExplosiveStaff


class ExplosiveStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExplosiveStaff
        fields = '__all__'
