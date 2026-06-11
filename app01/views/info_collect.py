import uuid
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from app01.forms.info_collect import InfoCollectForm
from app01.models.staff import Staff, StaffCert, StaffCertFile, CertType

def info_collect(request):
    """公开信息收集页面 — 数据写入 Staff 体系"""
    if request.method == 'POST':
        form = InfoCollectForm(request.POST, request.FILES)
        if form.is_valid():
            phone = form.cleaned_data['phone']

            # 1. 获取或创建 Staff
            staff, created = Staff.objects.get_or_create(
                phone=phone,
                defaults={'password': '888'}
            )

            # 2. 一寸照 → StaffCert(寸照) → StaffCertFile
            one_inch = request.FILES.get('one_inch_photo')
            if one_inch:
                ct_cun, _ = CertType.objects.get_or_create(name='寸照')
                sc_cun, _ = StaffCert.objects.get_or_create(
                    staff=staff, cert_type=ct_cun,
                    defaults={'cert_number': '', 'status': '有效'}
                )
                ext = os.path.splitext(one_inch.name)[1]
                one_inch.name = f"{uuid.uuid4().hex}{ext}"
                StaffCertFile.objects.create(cert=sc_cun, file=one_inch, file_type='一寸照')

            # 3. 身份证人像页 → StaffCert(身份证) → StaffCertFile(正面)
            front = request.FILES.get('front_photo')
            if front:
                ct_id, _ = CertType.objects.get_or_create(name='身份证')
                sc_id, _ = StaffCert.objects.get_or_create(
                    staff=staff, cert_type=ct_id,
                    defaults={'cert_number': '', 'status': '有效'}
                )
                ext = os.path.splitext(front.name)[1]
                front.name = f"{uuid.uuid4().hex}{ext}"
                StaffCertFile.objects.create(cert=sc_id, file=front, file_type='正面')

            # 4. 身份证国徽页 → StaffCert(身份证) → StaffCertFile(反面)
            back = request.FILES.get('back_photo')
            if back:
                ext = os.path.splitext(back.name)[1]
                back.name = f"{uuid.uuid4().hex}{ext}"
                StaffCertFile.objects.create(cert=sc_id, file=back, file_type='反面')

            return redirect('/home/info_collect/success/')
        return render(request, 'info_collect.html', {'form': form})
    form = InfoCollectForm()
    return render(request, 'info_collect.html', {'form': form})

def info_collect_success(request):
    """提交成功页"""
    return render(request, 'info_collect_success.html')

from app01.forms.info_collect import InfoSubmissionForm
from app01.models.info_collect import InfoSubmission


def info_submission_edit(request, pk):
    """Staff 编辑提交记录"""
    submission = get_object_or_404(InfoSubmission, pk=pk)
    if request.method == 'POST':
        form = InfoSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            import uuid, os
            s = form.save(commit=False)
            for field in ['front_photo', 'back_photo', 'one_inch_photo']:
                f = request.FILES.get(field)
                if f:
                    ext = os.path.splitext(f.name)[1]
                    f.name = f"{uuid.uuid4().hex}{ext}"
                    setattr(s, field, f)
            s.save()
            return redirect('/home/staff/info_submissions/')
        return render(request, 'staff/info_submission_edit.html', {'form': form, 'submission': submission})
    form = InfoSubmissionForm(instance=submission)
    return render(request, 'staff/info_submission_edit.html', {'form': form, 'submission': submission})

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app01.permissions import login_required


@login_required
def info_submissions_list(request):
    """Staff 信息提交列表"""
    data = InfoSubmission.objects.all().order_by("-created_at")
    paginator = Paginator(data, 20)
    page_number = request.GET.get("page", 1)
    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)
    return render(request, "staff/info_submissions_list.html", {
        "data": page_obj,
        "title": "信息收集记录",
        "is_paginated": True,
        "paginator": paginator,
        "page_obj": page_obj,
    })
