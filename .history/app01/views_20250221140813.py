from django.shortcuts import render, HttpResponse, redirect
from app01 import models
from app01 import modelform
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_protect

from app01.jiami import md5
from .func import *
from django_filters.views import FilterView
from django.views.generic import ListView
import pandas as pd

import sqlite3 as sl
from django.shortcuts import render
from django.apps import apps
from app01.models import ExplosiveInventoryItem
from app01.modelform import ExplosiveInventoryItemForm



def home(request):
    return render(request, "home.html")


def tu_add(request):
    title = 'tu'
    if request.method == 'POST':

        model_name = request.POST['model_name']
        files = request.FILES.getlist('file')  # 获取所有上传的文件

        for file in files:
            # 处理每个文件，例如保存到数据库或文件系统
            models.UploadedTu.objects.create(
                model_name=model_name, pdf_file=file)

        return redirect("/home/tu_list")

    else:
        model_names = models.UploadedTu.objects.values_list(
            'model_name', flat=True).distinct()
        return render(request, 'tu_add.html', {'model_names': model_names})


def tu_delete(request):

    id = request.GET.get('id')
    models.UploadedTu.objects.filter(id=str(id)).delete()
    return redirect("/home/tu_list")


def tu_list(request):

    title = 'tu'
    if request.method == "GET":

        data = models.UploadedTu.objects.values()[:100]

        # print(data)

        lst = dframe(data)
        cols = []

        for i in lst:
            cols.append({'age': i})

        return render(request, 'tu_list.html', {"data": data, "cols": cols, "title": title})


def upload_pdf(request):
    title = 'tu'
    if request.method == 'POST':

        model_name = request.POST['model_name']
        files = request.FILES.getlist('file')  # 获取所有上传的文件

        for file in files:
            # 处理每个文件，例如保存到数据库或文件系统
            models.UploadedPDF.objects.create(
                model_name=model_name, pdf_file=file)

        return redirect("/home/pdf_list")

    else:
        model_names = models.UploadedPDF.objects.values_list(
            'model_name', flat=True).distinct()
        return render(request, 'upload_pdf.html', {'model_names': model_names})


def pdf_delete(request):

    id = request.GET.get('id')
    models.UploadedPDF.objects.filter(id=str(id)).delete()
    return redirect("/home/pdf_list")


def pdf_list(request):

    title = 'pdf'
    if request.method == "GET":

        data = models.UploadedPDF.objects.values()[:100]

        # print(data)

        lst = dframe(data)
        cols = []

        for i in lst:
            cols.append({'age': i})

        return render(request, 'list_pdf.html', {"data": data, "cols": cols, "title": title})


# inventory333333333333333333333333##############################################################################################################
# inventory333333333333333333333333##############################################################################################################
# inventory333333333333333333333333##############################################################################################################
# inventory333333333333333333333333##############################################################################################################


def inventory_list(request):

    database = 'inventory'
    title = '出入库记录'
    if request.method == "GET":

        data = models.ExplosiveInventoryItem.objects.values()[:100]

        # print(data)

        lst = dframe(data)
        cols = []

        for i in lst:
            cols.append({'age': i})

        return render(request, 'list.html', {"data": data, "cols": cols, "数据库": database, '标题': title})


def inventory_create(request):
    title = '出入库记录'

    if request.method == "GET":

        form = ExplosiveInventoryItemForm()

        return render(request, 'create.html', {'form': form, '标题': title})

    if request.method == 'POST':
        form = ExplosiveInventoryItemForm(request.POST)

        if form.is_valid():

            form.save()

        else:

            form.errors
            return render(request, 'create.html', {'form': form, '标题': title})

    return redirect("/home/inventory_list")


def inventory_delete(request):

    id = request.GET.get('id')
    models.ExplosiveInventoryItem.objects.filter(id=str(id)).delete()
    return redirect("/home/inventory_list")


def inventory_edit(request):

    title = '出入库记录'
    id = request.GET.get('id')
    row_object = models.ExplosiveInventoryItem.objects.filter(
        id=str(id)).first()

    if request.method == "GET":

        form = modelform.ExplosiveInventoryItemForm(instance=row_object)

        return render(request, 'create.html', {"form": form, "标题": title})

    form = modelform.ExplosiveInventoryItemForm(
        data=request.POST, instance=row_object)

    if form.is_valid():

        form.save()
    else:
        title = '输入错误'
        form.errors
        return render(request, 'create.html', {'form': form})
    return redirect("/home/inventory_list")


# categorycontent------------------------------------------------------------------------------------------------------------------------------
# categorycontent------------------------------------------------------------------------------------------------------------------------------
# categorycontent------------------------------------------------------------------------------------------------------------------------------
# categorycontent------------------------------------------------------------------------------------------------------------------------------


def categorycontent_list(request):

    database = 'categorycontent'
    title = '民爆物品'
    if request.method == "GET":

        data = models.CategoryContent.objects.values()[:100]

        lst = dframe(data)
        cols = []

        for i in lst:
            cols.append({'age': i})

        return render(request, 'list.html', {"data": data, "cols": cols, "数据库": database, '标题': title})


def categorycontent_create(request):
    title = '民爆物品'

    if request.method == "GET":

        form = modelform.CategoryContentForm()

        return render(request, 'create.html', {'form': form, '标题': title})

    if request.method == 'POST':
        form = modelform. CategoryContentForm(request.POST)

        if form.is_valid():
            form.save()

        else:
            form.errors
            return render(request, 'create.html', {'form': form, '标题': title})

    return redirect("/home/categorycontent_list")


def categorycontent_delete(request):

    id = request.GET.get('id')
    models.CategoryContent.objects.filter(id=str(id)).delete()
    return redirect("/home/categorycontent_list")


def categorycontent_edit(request):
    title = '民爆物品'
    id = request.GET.get('id')
    row_object = models.CategoryContent.objects.filter(id=str(id)).first()

    if request.method == "GET":

        form = modelform.CategoryContentForm(instance=row_object)

        return render(request, 'create.html', {"form": form, "标题": title})

    form = modelform.CategoryContentForm(
        data=request.POST, instance=row_object)

    if form.is_valid():

        form.save()
    else:
        title = '输入错误'
        form.errors
        return render(request, 'create.html', {'form': form})
    return redirect("/home/categorycontent_list")


# ---------------------------------------------------------------------------------------


def upload_model(request):
    # 获取指定应用中的所有模型
    app_models = apps.get_app_config('app01').get_models()
    model_names = [model.__name__ for model in app_models]

    if request.method == 'POST':
        model_name = request.POST.get('model_name')
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            # 处理上传的 .xlsx 文件
            df = pd.read_excel(uploaded_file)
            df['password'] = df['password'].apply(lambda x: md5(str(x)))
            # 这里可以根据选择的模型表名进行相应的处理
            print(f"选择的模型表: {model_name}")
            print(df.head())
            try:
                with sl.connect('/Users/sunhongchen/lnjx2025/db.sqlite3') as con:
                    df.to_sql(f'app01_{model_name.lower()}',
                              con, index=False, if_exists='append')

                return HttpResponse("文件上传成功！")
            except Exception as e:
                return HttpResponse(f"文件上传失败: {str(e)}")

    return render(request, 'upload.html', {'model_names': model_names})


class StaffListView(FilterView, ListView):
    model = models.Admin
    template_name = 'staff_list.html'
    context_object_name = 'data'
    filterset_class = modelform.StaffFilter
    paginate_by = 100  # 每页显示的记录数
    ordering = ['id']  # 默认排序字段

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '员工列表'
        context['cols'] = [
            {'col_name': 'ID'},
            {'col_name': '标识'},
            {'col_name': '用户名'},
            {'col_name': '身份'},
            {'col_name': '部门'},
            {'col_name': '密码'},
            {'col_name': '图片'},
            {'col_name': '操作'},
            {'col_name': '证件'},
        ]
        return context


def staff_list(request):
    title = '管理员'

    if request.method == "GET":
        data = models.Admin.objects.values()

        # 将 QuerySet 转换为 DataFrame
        df = pd.DataFrame(list(data))

        # 根据 ident 列去重，保留最后一行
        df = df.drop_duplicates(subset='ident', keep='last')

        # 将 DataFrame 转换回列表
        data = df.to_dict('records')

        lst = dframe(data)

        cols = []
        for i in lst:
            cols.append({'col_name': i})

        return render(request, 'staff_list.html', {"data": data, "cols": cols, "title": title})

    return render(request, 'staff_list.html', {"title": title})


def staff_add(request):

    title = '新建员工信息'
    if request.method == "GET":
        form = modelform.Staff()
        return render(request, 'create.html', {"form": form, "标题": title})

    form = modelform.Staff(data=request.POST)

    if form.is_valid():

        form.save()
    else:
        title = '输入错误'
        form.errors
        return render(request, 'create.html', {"form": form, "标题": title})

    return redirect("/staff_list")


@最高权限
def staff_delete(request):

    id = request.GET.get('id')
    models.Admin.objects.filter(id=str(id)).delete()
    return redirect("/staff_list")


@资料员
def staff_edit(request):
    title = '员工信息编辑'
    id = request.GET.get('id')
    row_object = models.Admin.objects.filter(id=str(id)).first()
    print(models.Admin.objects.filter(id=str(id)).values())
    if request.method == "GET":

        form = modelform.Staff(instance=row_object)

        return render(request, 'change.html', {"form": form, "title": title})

    form = modelform.Staff(data=request.POST, instance=row_object)

    if form.is_valid():

        form.save()
    else:
        title = '输入错误'
        form.errors
        return render(request, 'change.html', {"form": form, "title": title})
    return redirect("/staff_list")
