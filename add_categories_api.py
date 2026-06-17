#!/usr/bin/env python3
"""在服务器 api_quiz.py 添加 quiz_categories 接口"""
import sys, os

server_path = "/root/django/app01/api_quiz.py"
urls_path = "/root/django/app01/api_urls.py"

# 读取
with open(server_path, "r") as f:
    content = f.read()

# 插入 quiz_categories 函数（在 quiz_qrcode 之前）
new_view = '''@api_view(["GET"])
@permission_classes([AllowAny])
def quiz_categories(request):
    """返回所有题库类别（去重）"""
    from .models.quiz import Question
    cats = Question.objects.values_list("category", flat=True).distinct().order_by("category")
    return JsonResponse({"categories": list(cats)})


'''
if "def quiz_categories" not in content:
    content = content.replace("def quiz_qrcode(request):", new_view + "def quiz_qrcode(request):")
    with open(server_path, "w") as f:
        f.write(content)
    print("✅ api_quiz.py 已添加 quiz_categories")
else:
    print("⏭️  quiz_categories 已存在")

# 添加路由
with open(urls_path, "r") as f:
    urls = f.read()

new_route = "    path('quiz/categories/', api_quiz.quiz_categories, name='quiz_categories'),\n"
if "quiz/categories/" not in urls:
    # 插入到第一个 quiz/ 路由后面
    urls = urls.replace(
        "    path('quiz/start/', api_quiz.quiz_start, name='quiz_start'),",
        "    path('quiz/start/', api_quiz.quiz_start, name='quiz_start'),\n" + new_route
    )
    with open(urls_path, "w") as f:
        f.write(urls)
    print("✅ api_urls.py 已添加路由")
else:
    print("⏭️  路由已存在")
