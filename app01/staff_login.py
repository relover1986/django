#%%
from django.shortcuts import render, redirect
from app01 import models


def staff_login(request):
    """Staff login view — login ID = phone, default password = 888"""
    if request.method == "GET":
        return render(request, 'staff_login.html', {'title': '人员登录'})

    phone = request.POST.get('phone', '').strip()
    password = request.POST.get('password', '').strip()

    if not phone:
        return render(request, 'staff_login.html', {
            'title': '人员登录',
            'error': '请输入手机号',
        })

    staff = models.Staff.objects.filter(phone=phone).first()
    if not staff:
        return render(request, 'staff_login.html', {
            'title': '人员登录',
            'error': '手机号或密码错误',
        })

    # 密码匹配：staff.password 空则对比 '888'，否则对比存储的密码
    if staff.password:
        if password != staff.password:
            return render(request, 'staff_login.html', {
                'title': '人员登录',
                'error': '手机号或密码错误',
            })
    else:
        if password != '888':
            return render(request, 'staff_login.html', {
                'title': '人员登录',
                'error': '手机号或密码错误',
            })

    # 写入 session
    request.session['info'] = {
        'ident': staff.phone,
        'name': staff.name,
        'role': 'staff',
        'department': staff.department,
    }
    request.session.set_expiry(60 * 60 * 24 * 7)  # 7天

    return redirect('/home/custom_quiz')
