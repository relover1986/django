# Auto-generated: imports all view functions from submodules
# home
from .home import home
# contract_labor
from .contract_labor import contractlabor_add, contractlabor_delete, contractlabor_list, contractlabor_export_zip
# photo
from .photo import api_photo_add, PhotoListAPIView, PhotoDetailAPIView, PhotoDeleteAPIView, PhotoUploadAPIView
from .photo import photo_add, photo_delete, photo_batch_delete, photo_list, generate_white_bg, photo_export_zip
# blasting_certificate
from .blasting_certificate import blastingcertificate_add, blastingcertificate_delete, blastingcertificate_list
from .blasting_certificate import blastingcertificate_export_xlsx, blastingcertificate_export_zip
# idcard
from .idcard import idcard_add, idcard_delete, api_idcard_add, api_idcard_list, idcard_list, idcard_export_zip

# ── 从 other.py 拆出的模块 ──
from .drawing import tu_add, tu_delete, tu_list
from .document import pdf_add, pdf_delete, pdf_list
from .inventory import inventory_list, inventory_add, inventory_delete, inventory_edit, inventory_export_xlsx
from .category import categorycontent_list, categorycontent_create, categorycontent_delete, categorycontent_edit
from .upload import upload_model
from .candidate import candidateprofile_add, candidateprofile_delete, candidateprofile_list
from .explosive_staff import explosivestaff_add, explosivestaff_delete, explosivestaff_list
from .explosive_staff import explosivestaff_export_xlsx, explosivestaff_export_zip
from .weighing import weighingrecord_add, weighingrecord_delete, weighingrecord_list
from .idcard import idcard_batch_upload

# staff
from .staff import StaffListView, staff_list, admin_add, admin_delete, admin_edit
from app01.permissions import login_required
from .staff import staff_add, staff_edit_v2, staff_delete_v2, staff_detail, staff_cert_add, staff_cert_delete
from .staff import cert_type_list, cert_type_add, cert_type_edit, cert_type_delete
# blasting_stats
from .blasting_stats import blasting_stats, blaster_list, blaster_add
from .blasting_stats import blasting_summary_list, blasting_summary_add, blasting_summary_delete, blasting_summary_assign_blaster
# blasting_site
from .blasting_site import blasting_site_photo_list, SignNetMulti, _load_sign_model
from .blasting_site import blasting_site_photo_add, blasting_site_low_conf, blasting_site_photo_delete
from .blasting_site import blasting_site_low_conf_delete, blasting_site_low_conf_submit
from .blasting_site import _preprocess_signature, _train_sse_events, blasting_site_train_signatures
# mine_card
from .mine_card import mine_card_index, mine_card_delete, mine_card_batch_delete, mine_card_update_photo
from .mine_card import _mine_card_workers_with_photos, mine_card_preview, mine_card_download
from .mine_card import _mine_card_parse_excel, _mine_card_generate_all_cards
