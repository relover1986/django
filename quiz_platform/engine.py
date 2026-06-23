"""刷题核心逻辑：概率权重抽题引擎"""
import random
from typing import List, Dict, Any
from django.db.models import QuerySet
from app01.models import Question

def select_weighted(queryset: QuerySet, count: int) -> List[Question]:
    """从 queryset 中按概率权重抽取 count 道题。权重 weight = 1.0 / (2^correct_streak)"""
    questions = list(queryset)
    if not questions:
        return []
    if len(questions) <= count:
        return questions
    weights = [q.weight for q in questions]
    total = sum(weights)
    if total == 0:
        return random.sample(questions, count)
    selected = []
    pool = list(zip(questions, weights))
    for _ in range(min(count, len(pool))):
        w_sum = sum(w for _, w in pool)
        r = random.random() * w_sum
        acc = 0.0
        for idx, (q, w) in enumerate(pool):
            acc += w
            if r <= acc:
                selected.append(q)
                pool.pop(idx)
                break
    return selected


def generate_round() -> Dict[str, Any]:
    """生成一轮刷题：5 单选 + 5 多选"""
    singles = Question.objects.filter(category__startswith="一建", question_type="单选题")
    multis = Question.objects.filter(category__startswith="一建", question_type="多选题")
    singles_chosen = select_weighted(singles, 5)
    multis_chosen = select_weighted(multis, 5)
    all_qs = singles_chosen + multis_chosen
    random.shuffle(singles_chosen)
    random.shuffle(multis_chosen)
    all_qs = singles_chosen + multis_chosen
    round_data = [{
        "id": q.id, "type": q.question_type, "question": q.question,
        "options": q.options, "tihao": q.tihao,
    } for q in all_qs]
    return {"questions": round_data, "question_ids": [q["id"] for q in round_data], "total": len(round_data)}


def check_answer(question_id: int, user_answer: str) -> Dict[str, Any]:
    """判题并更新 correct_streak / wrong_count"""
    from app01.models import Question, AnswerRecord
    try:
        q = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        return {"error": "题目不存在"}
    user_answer = user_answer.strip().upper()
    correct_answer = q.correct_answer.strip().upper()
    is_correct = (user_answer == correct_answer)
    streak_before = q.correct_streak
    if is_correct:
        q.correct_streak += 1
    else:
        q.correct_streak = 0
        q.wrong_count += 1
    q.save(update_fields=["correct_streak", "wrong_count"])
    AnswerRecord.objects.create(question=q, is_correct=is_correct, streak_before=streak_before)
    return {
        "id": q.id, "is_correct": is_correct, "user_answer": user_answer,
        "correct_answer": q.correct_answer, "analysis": q.analysis or "",
        "streak_after": q.correct_streak, "wrong_count": q.wrong_count,
    }
