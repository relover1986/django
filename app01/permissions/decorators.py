"""权限装饰器 - login_required, 资料员 等"""
from functools import wraps
from django.shortcuts import redirect, render


def login_required(view_func):
    """简易登录校验：检查 session 中是否有用户信息"""
    @wraps(view_func)
    def _wrapper(request, *args, **kwargs):
        if not request.session.get('info'):
            return redirect('/login/')
        return view_func(request, *args, **kwargs)
    return _wrapper


def 资料员(fun):
    """角色校验：仅允许「爆破工程技术人员」或「资料员」访问"""
    print(fun.__name__)
    def check(request):
        info = request.session.get('info')
        if info and ("爆破工程技术人员" in info.get('role', '') or "资料员" in info.get('role', '')):
            return fun(request)
        else:
            title = "没有权限!"
            return render(request, 'change.html', {"title": title})
    return check
