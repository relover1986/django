from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from functools import wraps
from app01 import models
from app01.forms import StaffForm, CertTypeForm, StaffCertForm, StaffCertFileForm


# ========== login_required decorator ==========
def login_required(view_func):
    """简易登录校验：检查 session 中是否有用户信息"""
    @wraps(view_func)
    def _wrapper(request, *args, **kwargs):
        if not request.session.get('info'):
            return redirect('/login/')
        return view_func(request, *args, **kwargs)
    return _wrapper


# ================================================================
#  人员管理 (Staff)
# ================================================================

@login_required
def staff_list(request):
    """人员列表：卡片 + 表格 + 分页 + 状态徽章"""
    search = request.GET.get('search', '').strip()
    queryset = models.Staff.objects.all().order_by('-created_at')
    if search:
        queryset = queryset.filter(name__icontains=search)

    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'staff_list_new.html', {
        'page_obj': page_obj,
        'search': search,
        'title': '人员管理',
        'is_paginated': page_obj.paginator.num_pages > 1,
        'paginator': page_obj.paginator,
    })


@login_required
def staff_add(request):
    """新增人员"""
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/staff/')
    else:
        form = StaffForm()
    return render(request, 'staff_form.html', {
        'form': form, 'title': '新增人员'
    })


@login_required
def staff_detail(request, pk):
    """人员详情：基本信息 + 证件列表 + 证件图片"""
    staff = get_object_or_404(models.Staff, pk=pk)
    certs = models.StaffCert.objects.filter(staff=staff).select_related('cert_type').order_by('-created_at')
    # 为每个证件预取附件
    for cert in certs:
        cert.files = models.StaffCertFile.objects.filter(cert=cert).order_by('uploaded_at')

    return render(request, 'staff_detail.html', {
        'staff': staff,
        'certs': certs,
        'title': f'{staff.name} - 人员详情',
    })


@login_required
def staff_edit(request, pk):
    """编辑人员"""
    staff = get_object_or_404(models.Staff, pk=pk)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            return redirect('/staff/')
    else:
        form = StaffForm(instance=staff)
    return render(request, 'staff_form.html', {
        'form': form, 'title': f'编辑人员 - {staff.name}'
    })


@login_required
def staff_delete(request, pk):
    """删除人员"""
    staff = get_object_or_404(models.Staff, pk=pk)
    staff.delete()
    return redirect('/staff/')


# ================================================================
#  人员证件 (StaffCert)
# ================================================================

@login_required
def staff_cert_add(request, pk):
    """为指定人员添加证件"""
    staff = get_object_or_404(models.Staff, pk=pk)
    if request.method == 'POST':
        form = StaffCertForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.staff = staff
            cert.save()
            return redirect('staff_detail', pk=staff.pk)
    else:
        form = StaffCertForm()
    return render(request, 'staff_cert_form.html', {
        'form': form, 'staff': staff, 'title': f'添加证件 - {staff.name}'
    })


@login_required
def staff_cert_delete(request, pk):
    """删除证件"""
    cert = get_object_or_404(models.StaffCert, pk=pk)
    staff_pk = cert.staff.pk
    cert.delete()
    return redirect('staff_detail', pk=staff_pk)


# ================================================================
#  证件类型管理 (CertType)
# ================================================================

@login_required
def cert_type_list(request):
    """证件类型列表"""
    queryset = models.CertType.objects.all().order_by('sort', 'id')
    return render(request, 'cert_type_list.html', {
        'cert_types': queryset,
        'title': '证件类型管理',
    })


@login_required
def cert_type_add(request):
    """新增证件类型"""
    if request.method == 'POST':
        form = CertTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/cert-type/')
    else:
        form = CertTypeForm()
    return render(request, 'cert_type_form.html', {
        'form': form, 'title': '新增证件类型'
    })


@login_required
def cert_type_edit(request, pk):
    """编辑证件类型"""
    cert_type = get_object_or_404(models.CertType, pk=pk)
    if request.method == 'POST':
        form = CertTypeForm(request.POST, instance=cert_type)
        if form.is_valid():
            form.save()
            return redirect('/cert-type/')
    else:
        form = CertTypeForm(instance=cert_type)
    return render(request, 'cert_type_form.html', {
        'form': form, 'title': f'编辑证件类型 - {cert_type.name}'
    })


@login_required
def cert_type_delete(request, pk):
    """删除证件类型"""
    cert_type = get_object_or_404(models.CertType, pk=pk)
    cert_type.delete()
    return redirect('/cert-type/')


@login_required
def staff_cert_file_add(request, pk):
    cert = get_object_or_404(models.StaffCert, pk=pk)
    staff = cert.staff
    if request.method == "POST":
        form = StaffCertFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save(commit=False)
            f.cert = cert
            f.save()
            return redirect("staff_detail", pk=staff.pk)
    else:
        form = StaffCertFileForm()
    return render(request, "staff_cert_file_add.html", {"form": form, "cert": cert, "staff": staff, "title": "上传证件附件"})


@login_required
def staff_cert_list(request):
    certs = models.StaffCert.objects.select_related("staff", "cert_type").order_by("-created_at")
    paginator = Paginator(certs, 20)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "staff_cert_list.html", {
        "page_obj": page, "title": "证件列表"
    })
