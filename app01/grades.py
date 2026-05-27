#%%
from django.shortcuts import render
from .models import UserAnswer, Admin
from django.db.models import Count, Max, Q
from collections import defaultdict

# 各类型总题量
TOTAL = {
    '爆破': 1606,
    '煤矿山井工': 644,
    '危险品装卸': 300,
}
TYPE_KEYS = list(TOTAL.keys())


def grades_new(request):
    # 1. 接受 GET 参数 type
    active_type = request.GET.get('type', '')

    # 2. 查答题记录，按 ident 分组统计
    qs = UserAnswer.objects.all()

    # 如果 type 非空，只保留该类型的答题记录
    if active_type:
        qs = qs.filter(ti_type=active_type)

    # 分组统计：每人各类型正确数 + 最后答题日期
    stats = (
        qs.values('ident')
        .annotate(
            score_爆破=Count('id', filter=Q(ti_type='爆破')),
            score_煤矿山井工=Count('id', filter=Q(ti_type='煤矿山井工')),
            score_危险品装卸=Count('id', filter=Q(ti_type='危险品装卸')),
            last_date=Max('date'),
        )
    )

    # 3. 联表取 username：ident -> username 映射
    admin_map = {a.ident: a.username for a in Admin.objects.all()}

    # 4. 组装行数据
    rows = []
    for s in stats:
        ident = s['ident']
        username = admin_map.get(ident, '')
        if not username:
            continue  # 没有姓名的记录跳过

        score_bp = s['score_爆破']
        score_mk = s['score_煤矿山井工']
        score_wx = s['score_危险品装卸']
        total = score_bp + score_mk + score_wx

        rows.append({
            'username': username,
            'total_score': total,
            'score_爆破': score_bp,
            'score_煤矿山井工': score_mk,
            'score_危险品装卸': score_wx,
            'last_date': s['last_date'],
            'remain_爆破': TOTAL['爆破'] - score_bp,
            'remain_煤矿山井工': TOTAL['煤矿山井工'] - score_mk,
            'remain_危险品装卸': TOTAL['危险品装卸'] - score_wx,
        })

    # 5. 按 username 排序
    rows.sort(key=lambda r: r['username'])

    # 6. 渲染模板
    return render(request, 'grades_table.html', {
        'rows': rows,
        'active_type': active_type,
    })
