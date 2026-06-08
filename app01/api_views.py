from rest_framework import viewsets
from .models import (
    Admin, Question,
    UserAnswer, LoginRecords, ExplosiveInventoryItem,
    CategoryContent, UploadedPDF, UploadedTu, UploadedZhaopian,
    IDCard, ContractLabor, Candidate, ExplosiveStaff,
    WeighingRecord, BlastingCertificate
)
from .serializers import (
    AdminSerializer, QuestionSerializer,
    UserAnswerSerializer, LoginRecordsSerializer,
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
    queryset = UploadedZhaopian.objects.all().order_by('-uploaded_at')
    serializer_class = UploadedZhaopianSerializer
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'uploaded_at']


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
    queryset = WeighingRecord.objects.all().order_by("-id")
    serializer_class = WeighingRecordSerializer
    filterset_fields = ['weight_number', 'truck_driver', 'forklift_driver']
    search_fields = ['weight_number', 'truck_driver']
    ordering_fields = '__all__'


class BlastingCertificateViewSet(viewsets.ModelViewSet):
    queryset = BlastingCertificate.objects.all()
    serializer_class = BlastingCertificateSerializer
    filterset_fields = ['certificate_number', 'name']
    search_fields = ['certificate_number', 'name']


from rest_framework.decorators import action
from rest_framework.response import Response
from app01.models.mine import Worker, JobType
from app01.serializers.mine_card import WorkerSerializer, JobTypeSerializer
import os as os2
from django.http import HttpResponse
from datetime import datetime


class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all().order_by("id")
    serializer_class = WorkerSerializer
    filterset_fields = ["department", "job_type"]
    search_fields = ["name"]

    def get_queryset(self):
        qs = super().get_queryset()
        dept = self.request.session.get("info", {}).get("department", "")
        if dept:
            qs = qs.filter(department=dept)
        return qs


    def perform_create(self, serializer):
        dept = self.request.session.get("info", {}).get("department", "")
        serializer.save(department=dept)

    @action(detail=True, methods=["post"], url_path="photo")
    def upload_photo(self, request, pk=None):
        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import InMemoryUploadedFile
        worker = self.get_object()
        uploaded = request.FILES.get("photo")
        if not uploaded:
            return Response({"error": "未提供照片"}, status=400)
        img = Image.open(uploaded)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        tw, th = 295, 413
        w, h = img.size
        scale = max(tw / w, th / h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        left = (img.width - tw) // 2
        top = (img.height - th) // 2
        img = img.crop((left, top, left + tw, top + th))
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=45, optimize=True, subsampling="4:2:0")
        buf.seek(0)
        new_file = InMemoryUploadedFile(buf, "photo", uploaded.name, "image/jpeg", buf.getbuffer().nbytes, None)
        worker.photo.save(f"{worker.name}_入井证.jpg", new_file, save=True)
        worker.refresh_from_db()
        return Response({"photo_url": worker.photo.url if worker.photo else None})

    @action(detail=False, methods=["post"], url_path="batch-delete")
    def batch_delete(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"error": "无 ID"}, status=400)
        workers = Worker.objects.filter(id__in=ids)
        for w in workers:
            if w.photo and os2.path.exists(w.photo.path):
                os2.remove(w.photo.path)
        deleted, _ = workers.delete()
        return Response({"deleted": deleted})

    @action(detail=False, methods=["post"], url_path="import-excel")
    def import_excel(self, request):
        from app01.services.card_service import parse_excel
        excel_file = request.FILES.get("excel")
        if not excel_file:
            return Response({"error": "未提供 Excel 文件"}, status=400)
        dept = request.session.get("info", {}).get("department", "")
        imported = parse_excel(excel_file, department=dept)
        return Response({"imported": imported})

    @action(detail=False, methods=["get"], url_path="preview")
    def preview(self, request):
        from app01.services.card_service import get_workers_with_photos, generate_all_cards
        dept = request.session.get("info", {}).get("department", "")
        workers = get_workers_with_photos(department=dept)
        if not workers:
            return Response({"sheets": [], "total": 0})
        from app01.image_utils import generate_sheets
        front_bufs, back_bufs = generate_all_cards(workers)
        sheets = generate_sheets(workers, front_bufs, back_bufs)
        return Response({"sheets": sheets, "total": len(workers)})

    @action(detail=False, methods=["get"], url_path="download")
    def download_zip(self, request):
        from app01.services.card_service import get_workers_with_photos, generate_all_cards
        dept = request.session.get("info", {}).get("department", "")
        workers = get_workers_with_photos(department=dept)
        if not workers:
            return Response({"error": "无数据"}, status=400)
        from app01.image_utils import generate_zip
        front_bufs, back_bufs = generate_all_cards(workers)
        zip_buf = generate_zip(workers, front_bufs, back_bufs)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        response = HttpResponse(zip_buf, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="入井标签_A4排版_{timestamp}.zip"'
        return response


class JobTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JobType.objects.all().order_by("name")
    serializer_class = JobTypeSerializer
