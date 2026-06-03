"""权限装饰器 - login_required, 资料员, 最高权限 等"""
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
    """角色校验：仅允许「爆破工程技术人员」或「资料员」访问（支持有参视图）"""
    @wraps(fun)
    def check(request, *args, **kwargs):
        info = request.session.get('info')
        if info and ("爆破工程技术人员" in info.get('role', '') or "资料员" in info.get('role', '')):
            return fun(request, *args, **kwargs)
        else:
            title = "没有权限!"
            return render(request, 'change.html', {"title": title})
    return check


def 最高权限(fun):
    """最高权限校验：仅 ident 为 000001 或 000002 可访问（支持有参视图）"""
    @wraps(fun)
    def check(request, *args, **kwargs):
        info = request.session.get('info')
        if info and info.get('ident') in ("000001", "000002"):
            return fun(request, *args, **kwargs)
        else:
            title = "没有权限!"
            return render(request, 'change.html', {"title": title})
    return check


def require_role(*roles):
    """通用角色校验装饰器（支持多个角色）

    用法: @require_role('爆破工程技术人员', '资料员')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapper(request, *args, **kwargs):
            info = request.session.get('info')
            if info and any(r in info.get('role', '') for r in roles):
                return view_func(request, *args, **kwargs)
            title = "没有权限!"
            return render(request, 'change.html', {"title": title})
        return _wrapper
    return decorator
