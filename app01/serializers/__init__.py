from .admin import AdminSerializer
from .quiz import (
    QuestionSerializer,
    UserAnswerSerializer, TihaoSerializer
)
from .auth import LoginRecordsSerializer
from .inventory import ExplosiveInventoryItemSerializer
from .category import CategoryContentSerializer
from .pdf import UploadedPDFSerializer
from .tu import UploadedTuSerializer
from .photo import UploadedZhaopianSerializer, PhotoUploadSerializer
from .idcard import IDCardSerializer
from .contract import ContractLaborSerializer
from .candidate import CandidateSerializer
from .explosive import ExplosiveStaffSerializer
from .weighing import WeighingRecordSerializer
from .blasting import BlastingCertificateSerializer

__all__ = [
    'AdminSerializer',
    'QuestionSerializer',
    'UserAnswerSerializer',
    'TihaoSerializer',
    'LoginRecordsSerializer',
    'ExplosiveInventoryItemSerializer',
    'CategoryContentSerializer',
    'UploadedPDFSerializer',
    'UploadedTuSerializer',
    'UploadedZhaopianSerializer',
    'PhotoUploadSerializer',
    'IDCardSerializer',
    'ContractLaborSerializer',
    'CandidateSerializer',
    'ExplosiveStaffSerializer',
    'WeighingRecordSerializer',
    'BlastingCertificateSerializer',
]
