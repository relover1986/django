from rest_framework import serializers
from app01.models.mine import Worker, JobType


class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = '__all__'


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
