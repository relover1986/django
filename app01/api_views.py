from rest_framework import viewsets
from .models import (
    Admin, Question,
    UserAnswer, Tihao, LoginRecords, ExplosiveInventoryItem,
    CategoryContent, UploadedPDF, UploadedTu, UploadedZhaopian,
    IDCard, ContractLabor, Candidate, ExplosiveStaff,
    WeighingRecord, BlastingCertificate
)
from .serializers import (
    AdminSerializer, QuestionSerializer,
    UserAnswerSerializer, TihaoSerializer, LoginRecordsSerializer,
    ExplosiveInventoryItemSerializer, CategoryContentSerializer,
    UploadedPDFSerializer, UploadedTuSerializer,
    UploadedZhaopianSerializer, IDCardSerializer,
    ContractLaborSerializer, CandidateSerializer,
    ExplosiveStaffSerializer, WeighingRecordSerializer,
    BlastingCertificateSerializer
)


class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    filterset_fields = ['ident', 'username', 'role', 'department']
    search_fields = ['username', 'ident', 'department']
    ordering_fields = '__all__'


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filterset_fields = ['category', 'question_type', 'tihao']
    search_fields = ['question_type', 'tihao']


class UserAnswerViewSet(viewsets.ModelViewSet):
    queryset = UserAnswer.objects.all()
    serializer_class = UserAnswerSerializer
    filterset_fields = ['ti_type', 'tihao', 'date', 'ident']
    ordering_fields = '__all__'


class TihaoViewSet(viewsets.ModelViewSet):
    queryset = Tihao.objects.all()
    serializer_class = TihaoSerializer


class LoginRecordsViewSet(viewsets.ModelViewSet):
    queryset = LoginRecords.objects.all()
    serializer_class = LoginRecordsSerializer
    filterset_fields = ['ip', 'ident', 'name', 'job', 'type', 'time']
    ordering_fields = ['time']


class ExplosiveInventoryItemViewSet(viewsets.ModelViewSet):
    queryset = ExplosiveInventoryItem.objects.all()
    serializer_class = ExplosiveInventoryItemSerializer
    filterset_fields = ['date', 'inventory_status', 'project_department', 'blaster']
    ordering_fields = '__all__'


class CategoryContentViewSet(viewsets.ModelViewSet):
    queryset = CategoryContent.objects.all()
    serializer_class = CategoryContentSerializer
    filterset_fields = ['category']
    search_fields = ['category', 'content']


class UploadedPDFViewSet(viewsets.ModelViewSet):
    queryset = UploadedPDF.objects.all()
    serializer_class = UploadedPDFSerializer
    filterset_fields = ['model_name']


class UploadedTuViewSet(viewsets.ModelViewSet):
    queryset = UploadedTu.objects.all()
    serializer_class = UploadedTuSerializer
    filterset_fields = ['model_name']


class UploadedZhaopianViewSet(viewsets.ModelViewSet):
    queryset = UploadedZhaopian.objects.all()
    serializer_class = UploadedZhaopianSerializer
    filterset_fields = ['name']
    search_fields = ['name']


class IDCardViewSet(viewsets.ModelViewSet):
    queryset = IDCard.objects.all()
    serializer_class = IDCardSerializer
    filterset_fields = ['name', 'id_number']
    search_fields = ['name', 'id_number']


class ContractLaborViewSet(viewsets.ModelViewSet):
    queryset = ContractLabor.objects.all()
    serializer_class = ContractLaborSerializer
    filterset_fields = ['name', 'id_number']
    search_fields = ['name', 'id_number']


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    filterset_fields = ['name', 'gender', 'mobile', 'position', 'education']
    search_fields = ['name', 'position']
    ordering_fields = '__all__'


class ExplosiveStaffViewSet(viewsets.ModelViewSet):
    queryset = ExplosiveStaff.objects.all()
    serializer_class = ExplosiveStaffSerializer
    filterset_fields = ['name', 'id_number', 'mobile']
    search_fields = ['name', 'id_number']


class WeighingRecordViewSet(viewsets.ModelViewSet):
    queryset = WeighingRecord.objects.all()
    serializer_class = WeighingRecordSerializer
    filterset_fields = ['weight_number', 'truck_driver', 'forklift_driver']
    search_fields = ['weight_number', 'truck_driver']
    ordering_fields = '__all__'


class BlastingCertificateViewSet(viewsets.ModelViewSet):
    queryset = BlastingCertificate.objects.all()
    serializer_class = BlastingCertificateSerializer
    filterset_fields = ['certificate_number', 'name']
    search_fields = ['certificate_number', 'name']
