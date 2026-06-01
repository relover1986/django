"""统计数据服务 - 爆破统计汇总"""
from collections import defaultdict
from app01 import models


def compute_blasting_stats():
    """雷管炸药台帐统计：按日期+班次+爆破员分组，班次合计
    
    返回 (rows, shift_totals, display_rows)
    """
    from utils import kg_to_box_package

    records = models.BlastingSummary.objects.all()

    groups = defaultdict(lambda: {'detonator': 0, 'explosive': 0, 'count': 0})
    shift_totals = defaultdict(lambda: {'detonator': 0, 'explosive': 0})

    for r in records:
        blaster = r.blaster or r.person or '未知'
        key = (r.date, r.shift or '—', blaster)
        groups[key]['detonator'] += r.detonator_count
        groups[key]['explosive'] += r.explosive_count
        groups[key]['count'] += 1
        sk = (r.date, r.shift or '—')
        shift_totals[sk]['detonator'] += r.detonator_count
        shift_totals[sk]['explosive'] += r.explosive_count

    rows = []
    shift_order = {'早':1,'早班':1,'白':2,'白班':2,'中':3,'中班':3,'晚':4,'晚班':4,'夜':5,'夜班':5}
    for (date, shift, blaster), vals in sorted(groups.items(), key=lambda x: (
        -int(x[0][0].replace('年','').replace('月','').replace('日','')) if '年' in x[0][0] else 0,
        shift_order.get(x[0][1], 99), x[0][2])):
        boxes, bags, _ = kg_to_box_package(vals['explosive'])
        rows.append({
            'date': date,
            'shift': shift,
            'blaster': blaster,
            'detonator': vals['detonator'],
            'explosive': vals['explosive'],
            'explosive_boxes': boxes,
            'explosive_bags': bags,
            'count': vals['count'],
        })

    display_rows = []
    prev_key = None
    for r in rows:
        cur_key = (r['date'], r['shift'])
        if prev_key and prev_key != cur_key:
            t = shift_totals[prev_key]
            sboxes, sbags, _ = kg_to_box_package(t['explosive'])
            display_rows.append({
                'is_summary': True, 'date': prev_key[0], 'shift': prev_key[1],
                'blaster': '合计', 'detonator': t['detonator'], 'explosive': t['explosive'],
                'explosive_boxes': sboxes, 'explosive_bags': sbags,
            })
        display_rows.append(r)
        prev_key = cur_key
    if prev_key:
        t = shift_totals[prev_key]
        sboxes, sbags, _ = kg_to_box_package(t['explosive'])
        display_rows.append({
            'is_summary': True, 'date': prev_key[0], 'shift': prev_key[1],
            'blaster': '合计', 'detonator': t['detonator'], 'explosive': t['explosive'],
            'explosive_boxes': sboxes, 'explosive_bags': sbags,
        })

    # 日期合并单元格
    date_counts = {}
    for r in display_rows:
        d = r['date']
        date_counts[d] = date_counts.get(d, 0) + 1
    date_done = set()
    for r in display_rows:
        d = r['date']
        if d not in date_done:
            r['date_rowspan'] = date_counts[d]
            date_done.add(d)
        else:
            r['date_rowspan'] = 0

    return display_rows
