from rest_framework import serializers
from app01.models import (
    QuestionType, JskjgQuestion, WxpzxQuestion,
    UserAnswer, Tihao
)


class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = '__all__'


class JskjgQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JskjgQuestion
        fields = '__all__'


class WxpzxQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WxpzxQuestion
        fields = '__all__'


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = '__all__'


class TihaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tihao
        fields = '__all__'
