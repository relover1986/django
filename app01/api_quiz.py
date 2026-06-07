"""
API: quiz start / submit
业务逻辑在服务端，Vue 只负责渲染和提交
"""
import pandas as pd
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from .models.quiz import Question, UserAnswer

CATEGORY_CONFIG = {
    "爆破": {"ti_type": "爆破"},
    "井工": {"ti_type": "非煤矿山井工"},
    "危装": {"ti_type": "危险品装卸"},
}

PICK_COUNTS = {"单选题": 5, "多选题": 5, "判断题": 10}


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def quiz_start(request):
    """开始答题：后端随机抽题，返回题目（不含正确答案）"""
    category = request.data.get("category", "爆破")
    cfg = CATEGORY_CONFIG.get(category, {"ti_type": category})
    ti_type = cfg["ti_type"]

    info = request.session.get("info", {})
    ident = info.get("ident", request.data.get("ident", ""))

    answered = set(
        UserAnswer.objects.filter(ident=ident, ti_type=ti_type)
        .values_list("tihao", flat=True)
    )

    df = pd.DataFrame(
        Question.objects.filter(category=category).values(
            "tihao", "question_type", "question", "options", "correct_answer"
        )
    )
    if df.empty:
        return JsonResponse({"error": "该类别暂无题目"}, status=400)

    df = df[~df["tihao"].isin(answered)]
    total_remaining = len(df)

    dfs = []
    for qtype, n_max in PICK_COUNTS.items():
        sub = df[df["question_type"] == qtype]
        n = min(len(sub), n_max)
        if n > 0:
            sub = sub.sample(n=n)
            dfs.append(sub)
    df = pd.concat(dfs) if dfs else pd.DataFrame()

    if df.empty:
        return JsonResponse({"error": "没有未答题目"}, status=400)

    df = df.reset_index(drop=True)
    seq = df.groupby("question_type").cumcount() + 1
    df["题号"] = df["question_type"].str.replace("题", "") + seq.astype(str)

    session_key = f"quiz_api_{category}"
    questions_data = df.to_dict(orient="records")
    request.session[session_key] = questions_data

    result = []
    for q in questions_data:
        # 后端补全空选项（判断题默认"对/错"）
        opts = q["options"]
        if not opts or not opts.strip():
            if q["question_type"] == "判断题":
                opts = "A.对 B.错"
        result.append({
            "session_key": session_key,
            "题号": q["题号"],
            "tihao": q["tihao"],
            "question_type": q["question_type"],
            "question": q["question"],
            "options": opts,
            "total_remaining": total_remaining,
        })
    return JsonResponse({"session_key": session_key, "questions": result})


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def quiz_submit(request):
    """提交答案：后端判分，写 UserAnswer，返回成绩"""
    import logging
    logger = logging.getLogger(__name__)
    session_key = request.data.get("session_key", "")
    answers = request.data.get("answers", {})
    info = request.session.get("info", {})
    logger.warning(f"[QUIZ_SUBMIT] session_key={session_key}, answers={len(answers)}, ident={info.get('ident','')}, session_keys={list(request.session.keys())}")

    quiz_data = request.session.get(session_key, [])
    if not quiz_data:
        logger.error(f"[QUIZ_SUBMIT] No quiz data for key={session_key}, session has keys: {list(request.session.keys())}")
        return JsonResponse({"error": "答题会话过期，请重新加载"}, status=400)

    cfg = None
    for key, val in CATEGORY_CONFIG.items():
        if f"quiz_api_{key}" == session_key:
            cfg = val
            break
    ti_type = cfg["ti_type"] if cfg else session_key.replace("quiz_api_", "")

    info = request.session.get("info", {})
    ident = info.get("ident", request.data.get("ident", ""))
    from datetime import date as dt_date
    today = dt_date.today().isoformat()

    df = pd.DataFrame(quiz_data)
    rows = []
    for _, q in df.iterrows():
        题号 = q["题号"]
        user_ans = answers.get(题号, "")
        if isinstance(user_ans, list):
            user_ans = "".join(user_ans)
        user_ans = str(user_ans).upper().strip()
        correct = q["correct_answer"]
        is_correct = user_ans == correct
        penalty = 0 if is_correct else (2 if q["question_type"] in ("多选题",) else 1)
        rows.append({
            "题号": 题号,
            "tihao": q["tihao"],
            "question": q["question"],
            "question_type": q["question_type"],
            "user_answer": user_ans,
            "correct_answer": correct,
            "is_correct": is_correct,
            "penalty": penalty,
        })

    result_df = pd.DataFrame(rows)
    correct_df = result_df[result_df["is_correct"] == True]

    if not correct_df.empty:
        objs = [
            UserAnswer(ti_type=ti_type, tihao=r["tihao"], date=today, ident=ident)
            for _, r in correct_df.iterrows()
        ]
        UserAnswer.objects.bulk_create(objs)

    total_deduct = int(result_df[result_df["is_correct"] == False]["penalty"].sum()) if len(result_df) > 0 else 0

    return JsonResponse({
        "total": len(result_df),
        "correct": len(correct_df),
        "penalty": total_deduct,
        "results": rows,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def quiz_stats(request):
    """答题统计：后端直接 count 数据库，返回每人已答题数和完成率"""
    from .models.quiz import Question, UserAnswer
    from .models.staff import Staff

    ti_type = request.GET.get("type", "")
    department_filter = request.GET.get("department", "")

    # 题库总数（按 category 对应 ti_type）
    cat_map = {"爆破": "爆破", "非煤矿山井工": "井工", "危险品装卸": "危装"}
    if ti_type:
        category = cat_map.get(ti_type, ti_type)
        total = Question.objects.filter(category=category).count()
    else:
        total = Question.objects.count()

    # 取所有在职员工（关联部门）
    staff_qs = Staff.objects.filter(status="在职").values("phone", "name", "department")
    if department_filter:
        staff_qs = staff_qs.filter(department=department_filter)

    # 按 ident(phone) 统计已答题数
    from django.db.models import Count
    ans_qs = UserAnswer.objects
    if ti_type:
        ans_qs = ans_qs.filter(ti_type=ti_type)
    ans_counts = dict(ans_qs.values_list("ident").annotate(cnt=Count("tihao", distinct=True)))

    rows = []
    for s in staff_qs:
        phone = s["phone"]
        answered = ans_counts.get(phone, 0)
        rate = round(answered / total * 100) if total > 0 else 0
        rows.append({
            "name": s["name"],
            "department": s["department"],
            "answered": answered,
            "total": total,
            "rate": min(rate, 100),
        })

    rows.sort(key=lambda r: -r["rate"])
    return JsonResponse({"data": rows})


@api_view(["GET"])
@permission_classes([AllowAny])
def quiz_qrcode(request):
    """返回 staff_login 二维码 PNG（base64）"""
    import qrcode, io, base64 as b64
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data("http://bxks.online/staff_login/")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return JsonResponse({"qr_base64": b64.b64encode(buf.getvalue()).decode()})


@api_view(["POST"])
@permission_classes([AllowAny])
def quiz_import(request):
    """导入题库（Excel）"""
    import pandas as pd
    from .models.quiz import Question

    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"success": False, "error": "未上传文件"}, status=400)

    name = file.name.lower()
    if not (name.endswith(".xlsx") or name.endswith(".xls")):
        return JsonResponse({"success": False, "error": "仅支持 .xlsx / .xls 文件"}, status=400)

    try:
        df = pd.read_excel(file)
    except Exception as e:
        return JsonResponse({"success": False, "error": f"文件解析失败: {str(e)}"}, status=400)

    required = {"category", "question_type", "question", "options", "correct_answer"}
    missing = required - set(df.columns)
    if missing:
        return JsonResponse({"success": False, "error": f"缺少字段: {', '.join(sorted(missing))}"}, status=400)

    valid_types = {"单选题", "多选题", "判断题"}
    bad_types = set(df["question_type"].dropna().unique()) - valid_types
    if bad_types:
        return JsonResponse({"success": False, "error": f"无效题型: {', '.join(str(x) for x in bad_types)}"}, status=400)

    objs = []
    errors = []
    for i, row in df.iterrows():
        try:
            cat = str(row.get("category", "")).strip()
            qt = str(row.get("question_type", "")).strip()
            ti = str(row.get("tihao", str(i + 1))).strip()
            q = str(row.get("question", "")).strip()
            opts = str(row.get("options", "")).strip()
            ans = str(row.get("correct_answer", "")).strip()
            if not q or not opts or not ans:
                errors.append(f"第{i+2}行: 题目/选项/答案不能为空")
                continue
            objs.append(Question(category=cat, question_type=qt, tihao=ti, question=q, options=opts, correct_answer=ans))
        except Exception as e:
            errors.append(f"第{i+2}行: {str(e)}")

    if objs:
        Question.objects.bulk_create(objs)

    msg = f"成功导入 {len(objs)} 条"
    if errors:
        msg += f"，{len(errors)} 条跳过"
    return JsonResponse({"success": True, "message": msg, "imported": len(objs), "errors": errors[:10]})
