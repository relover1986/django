"""导出文件服务 - ZIP打包、XLSX生成"""
import io
import os
import zipfile
from datetime import datetime

import pandas as pd
from django.conf import settings
from django.http import HttpResponse
from openpyxl import Workbook

from app01 import models


# =============================================================================
# staff — staff_cert_export_zip
# =============================================================================
def staff_cert_export_zip(dept, cert_type_id=None):
    """导出证件附件为ZIP"""
    from app01.models import StaffCert, StaffCertFile

    certs = StaffCert.objects.select_related("staff", "cert_type").filter(
        staff__department=dept
    )
    if cert_type_id:
        certs = certs.filter(cert_type_id=cert_type_id)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for cert in certs:
            files = StaffCertFile.objects.filter(cert=cert)
            for f in files:
                path = os.path.join(settings.MEDIA_ROOT, str(f.file))
                if os.path.exists(path):
                    arcname = f"{cert.staff.name}_{cert.cert_type.name}_{f.file_type}.jpg"
                    zf.write(path, arcname)

    buf.seek(0)
    return buf


# =============================================================================
# blasting_certificate — blastingcertificate_export_xlsx / _zip
# =============================================================================
def blastingcertificate_export_xlsx():
    """导出爆破证书数据为XLSX"""
    wb = Workbook()
    ws = wb.active
    ws.title = "爆破证书数据"

    headers = ["姓名", "证书编号"]
    ws.append(headers)
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 30

    certificates = models.BlastingCertificate.objects.all().values_list(
        "name", "certificate_number"
    )
    for cert in certificates:
        ws.append([cert[0], cert[1]])

    excel_io = io.BytesIO()
    wb.save(excel_io)
    excel_io.seek(0)
    return excel_io


def blastingcertificate_export_zip():
    """导出爆破证书照片为ZIP"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        certificates = models.BlastingCertificate.objects.all()
        for cert in certificates:
            cert_photo = cert.certificate_photo
            if cert_photo and cert_photo.storage.exists(cert_photo.name):
                zipf.writestr(
                    f"{cert.certificate_number}_{cert.name}.jpg",
                    cert_photo.read(),
                )

    zip_buffer.seek(0)
    return zip_buffer


# =============================================================================
# contract_labor — contractlabor_export_zip
# =============================================================================
def contractlabor_export_zip():
    """导出合同工劳动合同文件为ZIP"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        laborers = models.ContractLabor.objects.all()
        for laborer in laborers:
            contract_file = laborer.contract_file
            if contract_file and contract_file.storage.exists(contract_file.name):
                zipf.writestr(
                    f"{laborer.id_number}_{laborer.name}/劳动合同.docx",
                    contract_file.read(),
                )

    zip_buffer.seek(0)
    return zip_buffer


# =============================================================================
# other — inventory_export_xlsx / explosivestaff_export_xlsx / _zip
# =============================================================================
def inventory_export_xlsx():
    """导出库存数据为XLSX（含汇总）"""
    inventory_items = models.ExplosiveInventoryItem.objects.all().values(
        "id",
        "project_department",
        "blaster",
        "emulsion_explosive_32mm",
        "powdery_explosive_box_2",
        "sticky_explosive",
        "electronic_detonator_5m",
        "electronic_detonator_15m",
        "inventory_status",
        "detonating_device_quantity",
        "detonating_cord_length",
        "date",
    )

    df = pd.DataFrame(list(inventory_items))
    column_mapping = {
        "id": "序号",
        "project_department": "项目部",
        "blaster": "爆破员",
        "emulsion_explosive_32mm": "32乳化(公斤)",
        "powdery_explosive_box_2": "2号粉箱(公斤)",
        "sticky_explosive": "粘药(公斤)",
        "electronic_detonator_5m": "5米电子雷管(发)",
        "electronic_detonator_15m": "15米电子雷管(发)",
        "inventory_status": "库存状态",
        "detonating_device_quantity": "起爆具(个)",
        "detonating_cord_length": "导爆索长度",
        "date": "日期",
    }
    df.rename(columns=column_mapping, inplace=True)

    if "日期" in df.columns:
        df["日期"] = pd.to_datetime(df["日期"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.fillna("")

    # 汇总数据
    df_for_summary = df.copy()
    df_for_summary["日期"] = pd.to_datetime(df_for_summary["日期"]).dt.date
    numeric_columns = [
        "32乳化(公斤)",
        "2号粉箱(公斤)",
        "粘药(公斤)",
        "5米电子雷管(发)",
        "15米电子雷管(发)",
        "起爆具(个)",
        "导爆索长度",
    ]
    for col in numeric_columns:
        df_for_summary[col] = pd.to_numeric(df_for_summary[col], errors="coerce").fillna(0)

    summary_df = df_for_summary.groupby(
        ["项目部", "日期"], as_index=False
    )[numeric_columns].sum()
    summary_df["序号"] = "合计"
    summary_df["爆破员"] = ""
    summary_df["库存状态"] = "汇总数据"

    summary_df["2号粉箱包装"] = summary_df.apply(
        lambda row: f"{int(row['2号粉箱(公斤)'] // 24)}箱{int((row['2号粉箱(公斤)'] % 24) // 3)}包"
        if pd.notnull(row["2号粉箱(公斤)"]) else "",
        axis=1,
    )
    summary_df["32乳化包装"] = summary_df.apply(
        lambda row: f"{int(row['32乳化(公斤)'] // 24)}箱{int((row['32乳化(公斤)'] % 24) // 6)}包"
        if pd.notnull(row["32乳化(公斤)"]) else "",
        axis=1,
    )

    summary_df["日期"] = pd.to_datetime(summary_df["日期"])
    summary_df = summary_df.sort_values(
        by=["项目部", "日期"], ascending=[True, False]
    )
    summary_df["日期"] = summary_df["日期"].dt.strftime("%Y-%m-%d")

    original_columns = df.columns.tolist()
    if "2号粉箱(公斤)" in original_columns:
        idx = original_columns.index("2号粉箱(公斤)") + 1
        original_columns.insert(idx, "2号粉箱包装")
    if "32乳化(公斤)" in original_columns:
        idx = original_columns.index("32乳化(公斤)") + 1
        original_columns.insert(idx, "32乳化包装")
    for col in ["2号粉箱包装", "32乳化包装"]:
        if col not in df.columns:
            df[col] = ""

    df = df[original_columns]
    summary_df = summary_df[original_columns]
    del summary_df["序号"]
    del summary_df["爆破员"]
    del summary_df["库存状态"]

    excel_io = io.BytesIO()
    with pd.ExcelWriter(excel_io, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="原始数据")
        worksheet_raw = writer.sheets["原始数据"]
        for i in range(len(original_columns)):
            col_letter = chr(65 + i)
            worksheet_raw.column_dimensions[col_letter].width = 20

        summary_df.to_excel(writer, index=False, sheet_name="汇总数据")
        worksheet_summary = writer.sheets["汇总数据"]
        for i in range(len(original_columns)):
            col_letter = chr(65 + i)
            worksheet_summary.column_dimensions[col_letter].width = 15

    excel_io.seek(0)
    return excel_io


def explosivestaff_export_xlsx():
    """导出爆破员数据为XLSX"""
    wb = Workbook()
    ws = wb.active
    ws.title = "爆破员数据"

    headers = ["姓名", "身份证号码", "手机号", "银行卡号"]
    ws.append(headers)
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 20

    staffs = models.ExplosiveStaff.objects.all().values_list(
        "name", "id_number", "mobile", "bank_card_number"
    )
    for staff in staffs:
        ws.append([staff[0], staff[1], staff[2] or "", staff[3] or ""])

    excel_io = io.BytesIO()
    wb.save(excel_io)
    excel_io.seek(0)
    return excel_io


def explosivestaff_export_zip():
    """导出爆破员图片为ZIP"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        staffs = models.ExplosiveStaff.objects.all()
        for staff in staffs:
            fields = [
                "front_image",
                "back_image",
                "combined_image",
                "photo",
                "typeset_photo",
                "no_crime",
                "graduation",
            ]
            for field in fields:
                file = getattr(staff, field)
                if file and file.storage.exists(file.name):
                    zipf.writestr(
                        f"{staff.name}_{staff.id_number}/{field}.jpg",
                        file.read(),
                    )

    zip_buffer.seek(0)
    return zip_buffer
