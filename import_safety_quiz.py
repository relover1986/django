"""导入安全400题到 app01_question"""
import openpyxl
import os, sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from app01.models.quiz import Question

wb = openpyxl.load_workbook("/root/django/安全400题_清洗后.xlsx")
ws = wb.active

# 先查已有题目（按题目去重）
existing = set(Question.objects.filter(category="安全").values_list("question", flat=True))
print(f"已有「安全」题目: {len(existing)}")

# 读取 Excel
rows = []
for row in ws.iter_rows(min_row=2, values_only=True):
    cat, qtype, question, opts, answer = row
    if not question or question in existing:
        continue
    rows.append((cat, qtype, question, opts, answer))

print(f"新题: {len(rows)}")

# 生成题号（在已有最大题号后递增）
max_tihao = Question.objects.filter(category="安全").count()
print(f"起始题号: {max_tihao + 1}")

objs = []
for i, (cat, qtype, question, opts, answer) in enumerate(rows):
    tihao = str(max_tihao + i + 1)
    objs.append(Question(
        category=cat, question_type=qtype, tihao=tihao,
        question=question, options=opts or "", correct_answer=answer
    ))

if objs:
    Question.objects.bulk_create(objs)
    print(f"✅ 入库 {len(objs)} 条")
else:
    print("✅ 无新题")

wb.close()
