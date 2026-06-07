from .admin import AdminSerializer
from .quiz import (
    QuestionSerializer,
    UserAnswerSerializer
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
from .mine_card import WorkerSerializer, JobTypeSerializer

__all__ = [
    'AdminSerializer',
    'QuestionSerializer',
    'UserAnswerSerializer',
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
    'WorkerSerializer',
    'JobTypeSerializer',
]
