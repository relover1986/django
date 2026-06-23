import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from app01.models import Question, AnswerRecord
from .engine import generate_round, check_answer


def index(request):
    total = Question.objects.filter(category__startswith="一建").count()
    single_count = Question.objects.filter(category__startswith="一建", question_type="单选题").count()
    multi_count = Question.objects.filter(category__startswith="一建", question_type="多选题").count()
    wrong_count = Question.objects.filter(category__startswith="一建", wrong_count__gt=0).count()
    mastered_count = Question.objects.filter(category__startswith="一建", correct_streak__gte=3).count()
    return render(request, "quiz_platform/index.html", {
        "total_questions": total, "single_count": single_count,
        "multi_count": multi_count, "wrong_count": wrong_count,
        "mastered_count": mastered_count,
    })


def start_round(request):
    round_data = generate_round()
    request.session["current_round"] = {
        "question_ids": round_data["question_ids"], "total": round_data["total"],
    }
    request.session.modified = True
    return render(request, "quiz_platform/round.html", {
        "questions_json": json.dumps(round_data["questions"], ensure_ascii=False),
        "total": round_data["total"],
    })


@require_http_methods(["POST"])
def submit_round(request):
    data = json.loads(request.body)
    answers = data.get("answers", {})
    round_info = request.session.get("current_round", {})
    question_ids = round_info.get("question_ids", [])
    results = []
    correct_count = 0
    for qid in question_ids:
        user_ans = answers.get(str(qid), "")
        result = check_answer(qid, user_ans)
        results.append(result)
        if result.get("is_correct"):
            correct_count += 1
    if "current_round" in request.session:
        del request.session["current_round"]
    return JsonResponse({
        "results": results, "correct_count": correct_count,
        "total": len(results), "score": round(correct_count / len(results) * 100) if results else 0,
    })


def wrong_book(request):
    filter_type = request.GET.get("type", "wrong")
    chapter = request.GET.get("chapter", "")
    qs = Question.objects.filter(category__startswith="一建")
    if filter_type == "wrong":
        qs = qs.filter(wrong_count__gt=0)
    elif filter_type == "mastered":
        qs = qs.filter(correct_streak__gte=3)
    if chapter:
        qs = qs.filter(chapter=chapter)
    qs = qs.order_by("-wrong_count", "correct_streak")
    chapters = Question.objects.filter(category__startswith="一建").exclude(chapter__isnull=True).exclude(chapter="")\
        .values_list("chapter", flat=True).distinct().order_by("chapter")
    return render(request, "quiz_platform/wrong_book.html", {
        "questions": qs, "filter_type": filter_type,
        "current_chapter": chapter, "chapters": chapters,
    })


@require_http_methods(["POST"])
def update_chapter(request):
    data = json.loads(request.body)
    qid = data.get("id")
    chapter = data.get("chapter", "").strip()
    try:
        q = Question.objects.get(pk=qid)
        q.chapter = chapter if chapter else None
        q.save(update_fields=["chapter"])
        return JsonResponse({"ok": True})
    except Question.DoesNotExist:
        return JsonResponse({"error": "题目不存在"}, status=404)


@require_http_methods(["POST"])
def reset_question(request):
    data = json.loads(request.body)
    qid = data.get("id")
    try:
        q = Question.objects.get(pk=qid)
        q.correct_streak = 0
        q.save(update_fields=["correct_streak"])
        return JsonResponse({"ok": True})
    except Question.DoesNotExist:
        return JsonResponse({"error": "题目不存在"}, status=404)


def stats(request):
    from django.db.models import Count, Avg, Q
    from django.utils import timezone
    from datetime import timedelta
    total = Question.objects.filter(category__startswith="一建").count()
    wrong_count = Question.objects.filter(category__startswith="一建", wrong_count__gt=0).count()
    mastered_count = Question.objects.filter(category__startswith="一建", correct_streak__gte=3).count()
    avg_streak = Question.objects.filter(category__startswith="一建").aggregate(avg=Avg("correct_streak"))["avg"] or 0
    type_stats = []
    for qt in ["单选题", "多选题"]:
        qs = Question.objects.filter(category__startswith="一建", question_type=qt)
        t = qs.count()
        w = qs.filter(wrong_count__gt=0).count()
        m = qs.filter(correct_streak__gte=3).count()
        type_stats.append({"question_type": qt, "total": t, "wrong": w, "mastered": m})
    chapter_stats = (
        Question.objects.filter(category__startswith="一建").exclude(chapter__isnull=True).exclude(chapter="")
        .values("chapter").annotate(total=Count("id"), wrong=Count("id", filter=Q(wrong_count__gt=0)))
        .order_by("-wrong")
    )
    today = timezone.now().date()
    daily_stats = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        records = AnswerRecord.objects.filter(created_at__date=day)
        total_rec = records.count()
        correct_rec = records.filter(is_correct=True).count()
        daily_stats.append({
            "date": day.strftime("%m-%d"), "total": total_rec,
            "correct": correct_rec, "rate": round(correct_rec / total_rec * 100) if total_rec else 0,
        })
    return render(request, "quiz_platform/stats.html", {
        "total": total, "wrong_count": wrong_count, "mastered_count": mastered_count,
        "avg_streak": round(avg_streak, 1), "type_stats": type_stats,
        "chapter_stats": chapter_stats, "daily_stats": daily_stats,
    })


def qa_page(request):
    return render(request, "quiz_platform/qa.html")


@csrf_exempt
def qa_ask(request):
    data = json.loads(request.body)
    question = data.get("question", "").strip()
    if not question:
        return JsonResponse({"error": "请输入问题"}, status=400)
    from .qa_engine import ask
    result = ask(question)
    return JsonResponse(result)
