from rest_framework import serializers
from app01.models import UploadedZhaopian


class UploadedZhaopianSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedZhaopian
        fields = ['id', 'name', 'photo', 'rotated_photo', 'blue_background', 'red_background', 'white_background', 'white_bg_single', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            for field in ['photo', 'rotated_photo', 'blue_background', 'red_background', 'white_background', 'white_bg_single']:
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
