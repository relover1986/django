#%%
from django.shortcuts import render, redirect
from .models import QuestionType, UserAnswer, JskjgQuestion, WxpzxQuestion
import pandas as pd
import random
import arrow
import sqlite3 as sl
from pathlib import Path

BASE = Path(__file__).parent.parent
def _get_opt_text(options_str: str, answer: str) -> str:
    """提取选项文字，支持 A.xxx / A xxx / Axxx 格式，支持多选 ABC"""
    if not answer:
        return ""
    results = []
    for ch in answer:
        for opt in options_str.split():
            clean = opt.strip()
            if not clean:
                continue
            if clean[0] == ch:
                txt = clean[1:].lstrip(". \t")
                results.append(txt)
                break
    return " | ".join(results)

def ti_new(request):
    title = "辽宁捷祥民用爆破三大员培训题库"
    date = arrow.now().shift(days=0).format("YYYY-MM-DD")
    username = request.session["info"]["name"]
    ident = request.session["info"]["ident"]

    if request.method == "GET":
        data = QuestionType.objects.values("tihao", "question_type", "question", "options", "correct_answer")
        df = pd.DataFrame(data)

        answered = UserAnswer.objects.values("tihao").filter(ident=ident, ti_type="爆破")
        if answered.exists():
            df_answered = pd.DataFrame(answered)
            df = df.merge(df_answered, on="tihao", how="left", indicator=True)
            df = df[df["_merge"] == "left_only"].drop(columns=["_merge"])

        df.columns = ["tihao", "题型", "题目", "选项", "正确答案"]
        n_all = len(df)
        dfs = []
        for qtype, n_max in [("单选题", 5), ("多选题", 5), ("判断题", 10)]:
            sub = df[df["题型"] == qtype]
            n = min(len(sub), n_max)
            if n > 0:
                sub = sub.sample(n=n)
                sub["序号"] = range(1, n + 1)
                sub["题号"] = qtype.replace("题", "") + sub["序号"].astype(str)
                dfs.append(sub)
        df = pd.concat(dfs) if dfs else pd.DataFrame()
        questions = df.to_dict(orient="records")

        # Store in session for POST scoring
        request.session["quiz_data"] = questions

        context = {
            "title": f"{title} -- {username} 还有{n_all}题",
            "questions": questions,
        }
        return render(request, "baopo_ti_new.html", context)

    # POST: scoring
    quiz_data = request.session.get("quiz_data", [])
    if not quiz_data:
        return redirect("/home/baopo_ti_new")

    df = pd.DataFrame(quiz_data)
    # Rebuild 题号 mapping like change.py does
    df["题号"] = df["题型"].str.replace("题", "") + df["序号"].astype(str)

    # Read submitted answers
    rows = []
    for _, q in df.iterrows():
        tihao = q["题号"]
        answer = request.POST.getlist(tihao)
        answer = "".join(answer)
        rows.append({"题号": tihao, "我的答案": answer, "tihao": q["tihao"],
                      "题目": q["题目"], "选项": q["选项"], "正确答案": q["正确答案"], "题型": q["题型"],
                      "我的答案文字": _get_opt_text(q["选项"], answer),
                      "正确答案文字": _get_opt_text(q["选项"], q["正确答案"])})

    result_df = pd.DataFrame(rows)
    result_df["我的答案"] = result_df["我的答案"].str.replace(r"[^a-zA-Z0-9\u4e00-\u9fa5]", "", regex=True)
    result_df["得分"] = "正确"
    result_df.loc[result_df["我的答案"] != result_df["正确答案"], "得分"] = "错误"

    # Save correct answers to UserAnswer
    correct = result_df[result_df["得分"] == "正确"]
    if not correct.empty:
        records = correct[["tihao"]].copy()
        records["ti_type"] = "爆破"
        records["date"] = date
        records["ident"] = ident
        objs = []
        for _, r in records.iterrows():
            objs.append(UserAnswer(ti_type=r["ti_type"], tihao=r["tihao"],
                                   date=r["date"], ident=r["ident"]))
        UserAnswer.objects.bulk_create(objs)

    # Wrong answers for display
    wrong = result_df[result_df["得分"] == "错误"].copy()
    wrong["分值"] = 1
    wrong.loc[wrong["题号"].str.contains("多选"), "分值"] = 2
    total_deduct = wrong["分值"].sum() if not wrong.empty else 0

    wrong_list = wrong.to_dict(orient="records") if not wrong.empty else []
    correct_list = result_df[result_df["得分"] == "正确"].to_dict(orient="records") if not result_df[result_df["得分"] == "正确"].empty else []

    return render(request, "result_new.html", {
        "title": f"扣分 -- {total_deduct}",
        "total": len(result_df),
        "correct": len(correct),
        "wrong": total_deduct,
        "wrong_list": wrong_list,
        "correct_list": correct_list,
        "reload_url": "/home/baopo_ti_new_reload",
        "continue_url": "/home/baopo_ti_new",
    })

def ti_new_reload(request):
    if "quiz_data" in request.session:
        del request.session["quiz_data"]
    return redirect("/home/baopo_ti_new")


def jskjgti_new(request):
    title = "辽宁捷祥非煤矿山井工培训题库"
    date = arrow.now().shift(days=0).format("YYYY-MM-DD")
    username = request.session["info"]["name"]
    ident = request.session["info"]["ident"]

    if request.method == "GET":
        data = JskjgQuestion.objects.values("tihao", "question_type", "question", "options", "correct_answer")
        df = pd.DataFrame(data)

        answered = UserAnswer.objects.values("tihao").filter(ident=ident)
        if answered.exists():
            df_answered = pd.DataFrame(answered)
            df = df.merge(df_answered, on="tihao", how="left", indicator=True)
            df = df[df["_merge"] == "left_only"].drop(columns=["_merge"])

        df.columns = ["tihao", "题型", "题目", "选项", "正确答案"]
        n_all = len(df)
        dfs = []
        for qtype, n_max in [("单选题", 5), ("多选题", 5), ("判断题", 10)]:
            sub = df[df["题型"] == qtype]
            n = min(len(sub), n_max)
            if n > 0:
                sub = sub.sample(n=n)
                sub["序号"] = range(1, n + 1)
                sub["题号"] = qtype.replace("题", "") + sub["序号"].astype(str)
                dfs.append(sub)
        df = pd.concat(dfs) if dfs else pd.DataFrame()
        questions = df.to_dict(orient="records")

        # Store in session for POST scoring
        request.session["jskjg_quiz_data"] = questions

        context = {
            "title": f"{title} -- {username} 还有{n_all}题",
            "questions": questions,
        }
        return render(request, "baopo_ti_new.html", context)

    # POST: scoring
    quiz_data = request.session.get("jskjg_quiz_data", [])
    if not quiz_data:
        return redirect("/home/jskjgti_new")

    df = pd.DataFrame(quiz_data)
    # Rebuild 题号 mapping like change.py does
    df["题号"] = df["题型"].str.replace("题", "") + df["序号"].astype(str)

    # Read submitted answers
    rows = []
    for _, q in df.iterrows():
        tihao = q["题号"]
        answer = request.POST.getlist(tihao)
        answer = "".join(answer)
        rows.append({"题号": tihao, "我的答案": answer, "tihao": q["tihao"],
                      "题目": q["题目"], "选项": q["选项"], "正确答案": q["正确答案"], "题型": q["题型"]})

    result_df = pd.DataFrame(rows)
    result_df["我的答案"] = result_df["我的答案"].str.replace(r"[^a-zA-Z0-9\u4e00-\u9fa5]", "", regex=True)
    result_df["得分"] = "正确"
    result_df.loc[result_df["我的答案"] != result_df["正确答案"], "得分"] = "错误"

    # Save correct answers to UserAnswer
    correct = result_df[result_df["得分"] == "正确"]
    if not correct.empty:
        records = correct[["tihao"]].copy()
        records["ti_type"] = "非煤矿山井工"
        records["date"] = date
        records["ident"] = ident
        objs = []
        for _, r in records.iterrows():
            objs.append(UserAnswer(ti_type=r["ti_type"], tihao=r["tihao"],
                                   date=r["date"], ident=r["ident"]))
        UserAnswer.objects.bulk_create(objs)

    # Wrong answers for display
    wrong = result_df[result_df["得分"] == "错误"].copy()
    wrong["分值"] = 1
    wrong.loc[wrong["题号"].str.contains("多选"), "分值"] = 2
    total_deduct = wrong["分值"].sum() if not wrong.empty else 0

    wrong_list = wrong.to_dict(orient="records") if not wrong.empty else []
    correct_list = result_df[result_df["得分"] == "正确"].to_dict(orient="records") if not result_df[result_df["得分"] == "正确"].empty else []

    return render(request, "result_new.html", {
        "title": f"扣分 -- {total_deduct}",
        "total": len(result_df),
        "correct": len(correct),
        "wrong": total_deduct,
        "wrong_list": wrong_list,
        "correct_list": correct_list,
        "reload_url": "/home/jskjgti_new_reload",
        "continue_url": "/home/jskjgti_new",
    })


def jskjgti_new_reload(request):
    if "jskjg_quiz_data" in request.session:
        del request.session["jskjg_quiz_data"]
    return redirect("/home/jskjgti_new")


def wxpzxti_new(request):
    title = "辽宁捷祥危险品装卸培训题库"
    date = arrow.now().shift(days=0).format("YYYY-MM-DD")
    username = request.session["info"]["name"]
    ident = request.session["info"]["ident"]

    if request.method == "GET":
        data = WxpzxQuestion.objects.values("tihao", "question_type", "question", "options", "correct_answer")
        df = pd.DataFrame(data)

        answered = UserAnswer.objects.values("tihao").filter(ident=ident)
        if answered.exists():
            df_answered = pd.DataFrame(answered)
            df = df.merge(df_answered, on="tihao", how="left", indicator=True)
            df = df[df["_merge"] == "left_only"].drop(columns=["_merge"])

        df.columns = ["tihao", "题型", "题目", "选项", "正确答案"]
        n_all = len(df)
        dfs = []
        for qtype, n_max in [("单选题", 5), ("多选题", 5), ("判断题", 10)]:
            sub = df[df["题型"] == qtype]
            n = min(len(sub), n_max)
            if n > 0:
                sub = sub.sample(n=n)
                sub["序号"] = range(1, n + 1)
                sub["题号"] = qtype.replace("题", "") + sub["序号"].astype(str)
                dfs.append(sub)
        df = pd.concat(dfs) if dfs else pd.DataFrame()
        questions = df.to_dict(orient="records")

        # Store in session for POST scoring
        request.session["wxpzx_quiz_data"] = questions

        context = {
            "title": f"{title} -- {username} 还有{n_all}题",
            "questions": questions,
        }
        return render(request, "baopo_ti_new.html", context)

    # POST: scoring
    quiz_data = request.session.get("wxpzx_quiz_data", [])
    if not quiz_data:
        return redirect("/home/wxpzxti_new")

    df = pd.DataFrame(quiz_data)
    # Rebuild 题号 mapping like change.py does
    df["题号"] = df["题型"].str.replace("题", "") + df["序号"].astype(str)

    # Read submitted answers
    rows = []
    for _, q in df.iterrows():
        tihao = q["题号"]
        answer = request.POST.getlist(tihao)
        answer = "".join(answer)
        rows.append({"题号": tihao, "我的答案": answer, "tihao": q["tihao"],
                      "题目": q["题目"], "选项": q["选项"], "正确答案": q["正确答案"], "题型": q["题型"]})

    result_df = pd.DataFrame(rows)
    result_df["我的答案"] = result_df["我的答案"].str.replace(r"[^a-zA-Z0-9\u4e00-\u9fa5]", "", regex=True)
    result_df["得分"] = "正确"
    result_df.loc[result_df["我的答案"] != result_df["正确答案"], "得分"] = "错误"

    # Save correct answers to UserAnswer
    correct = result_df[result_df["得分"] == "正确"]
    if not correct.empty:
        records = correct[["tihao"]].copy()
        records["ti_type"] = "危险品装卸"
        records["date"] = date
        records["ident"] = ident
        objs = []
        for _, r in records.iterrows():
            objs.append(UserAnswer(ti_type=r["ti_type"], tihao=r["tihao"],
                                   date=r["date"], ident=r["ident"]))
        UserAnswer.objects.bulk_create(objs)

    # Wrong answers for display
    wrong = result_df[result_df["得分"] == "错误"].copy()
    wrong["分值"] = 1
    wrong.loc[wrong["题号"].str.contains("多选"), "分值"] = 2
    total_deduct = wrong["分值"].sum() if not wrong.empty else 0

    wrong_list = wrong.to_dict(orient="records") if not wrong.empty else []
    correct_list = result_df[result_df["得分"] == "正确"].to_dict(orient="records") if not result_df[result_df["得分"] == "正确"].empty else []

    return render(request, "result_new.html", {
        "title": f"扣分 -- {total_deduct}",
        "total": len(result_df),
        "correct": len(correct),
        "wrong": total_deduct,
        "wrong_list": wrong_list,
        "correct_list": correct_list,
        "reload_url": "/home/wxpzxti_new_reload",
        "continue_url": "/home/wxpzxti_new",
    })


def wxpzxti_new_reload(request):
    if "wxpzx_quiz_data" in request.session:
        del request.session["wxpzx_quiz_data"]
    return redirect("/home/wxpzxti_new")
