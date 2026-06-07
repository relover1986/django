from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'admins', api_views.AdminViewSet)
router.register(r'questions', api_views.QuestionViewSet)
router.register(r'user-answers', api_views.UserAnswerViewSet)
router.register(r'login-records', api_views.LoginRecordsViewSet)
router.register(r'inventory-items', api_views.ExplosiveInventoryItemViewSet)
router.register(r'category-contents', api_views.CategoryContentViewSet)
router.register(r'pdfs', api_views.UploadedPDFViewSet)
router.register(r'tus', api_views.UploadedTuViewSet)
router.register(r'photos', api_views.UploadedZhaopianViewSet)
router.register(r'idcards', api_views.IDCardViewSet)
router.register(r'contract-labors', api_views.ContractLaborViewSet)
router.register(r'candidates', api_views.CandidateViewSet)
router.register(r'explosive-staff', api_views.ExplosiveStaffViewSet)
router.register(r'weighing-records', api_views.WeighingRecordViewSet)
router.register(r'blasting-certificates', api_views.BlastingCertificateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

from . import api_quiz

urlpatterns += [
    path('quiz/start/', api_quiz.quiz_start, name='quiz_start'),
    path('quiz/submit/', api_quiz.quiz_submit, name='quiz_submit'),
    path('quiz/stats/', api_quiz.quiz_stats, name='quiz_stats'),
    path('quiz/qrcode/', api_quiz.quiz_qrcode, name='quiz_qrcode'),
    path('quiz/import/', api_quiz.quiz_import, name='quiz_import'),
]