from rest_framework import serializers
from .models import (
    Admin, QuestionType, JskjgQuestion, WxpzxQuestion,
    UserAnswer, Tihao, LoginRecords, ExplosiveInventoryItem,
    CategoryContent, UploadedPDF, UploadedTu, UploadedZhaopian,
    IDCard, ContractLabor, Candidate, ExplosiveStaff,
    WeighingRecord, BlastingCertificate
)


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'


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


class LoginRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginRecords
        fields = '__all__'


class ExplosiveInventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExplosiveInventoryItem
        fields = '__all__'


class CategoryContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryContent
        fields = '__all__'


class UploadedPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedPDF
        fields = '__all__'


class UploadedTuSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedTu
        fields = '__all__'


class UploadedZhaopianSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedZhaopian
        fields = ['id', 'name', 'photo', 'rotated_photo', 'blue_background', 'red_background', 'white_background', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            for field in ['photo', 'rotated_photo', 'blue_background', 'red_background', 'white_background']:
                if data.get(field):
                    data[field] = request.build_absolute_uri(data[field])
        return data


class PhotoUploadSerializer(serializers.Serializer):
    file = serializers.ImageField(
        allow_null=False,
        help_text='上传的图片文件'
    )
    model_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
        help_text='自定义文件名（单张图片时有效）'
    )


class IDCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = IDCard
        fields = '__all__'


class ContractLaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractLabor
        fields = '__all__'


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'


class ExplosiveStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExplosiveStaff
        fields = '__all__'


class WeighingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeighingRecord
        fields = '__all__'


class BlastingCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlastingCertificate
        fields = '__all__'
