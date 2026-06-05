from rest_framework import serializers
from app01.models import Question, UserAnswer, Tihao


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = '__all__'


class TihaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tihao
        fields = '__all__'
