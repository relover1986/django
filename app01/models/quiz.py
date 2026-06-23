"""Models: quiz domain + 刷题引擎"""
import re, os, uuid
from django.db import models

# ── 题目模型 ──────────────────────────────────

class Question(models.Model):
    category = models.CharField(max_length=10, verbose_name="题库类别", help_text="爆破/井工/危装")
    question_type = models.CharField(max_length=20, verbose_name="题型")
    tihao = models.CharField(max_length=20, verbose_name="题号")
    question = models.TextField(verbose_name="题目")
    options = models.CharField(max_length=200, verbose_name="选项")
    correct_answer = models.CharField(max_length=20, verbose_name="正确答案")
    analysis = models.TextField(verbose_name="解析", blank=True, default="")

    # 刷题引擎字段（一建矿业刷题用）
    chapter = models.CharField("所属章节", max_length=10, blank=True, null=True, db_index=True)
    correct_streak = models.IntegerField("正确连击数", default=0)
    wrong_count = models.IntegerField("累计错误次数", default=0)

    class Meta:
        db_table = "app01_question"
        verbose_name = "题库"

    def __str__(self):
        return f"[{self.category}] {self.question_type} 题{self.tihao}"

    @property
    def weight(self) -> float:
        """概率权重：正确连击数越高，权重越低"""
        return 1.0 / (2 ** self.correct_streak)

    @property
    def is_mastered(self) -> bool:
        """是否已掌握（正确连击>=3）"""
        return self.correct_streak >= 3

class UserAnswer(models.Model):
    ti_type = models.CharField(max_length=20)
    tihao = models.CharField(max_length=20)
    date = models.DateField()
    ident = models.CharField(max_length=20)

# ── 刷题记录模型 ────────────────────────────

class AnswerRecord(models.Model):
    """答题记录"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answer_records")
    is_correct = models.BooleanField("是否正确")
    streak_before = models.IntegerField("答题前正确连击数")
    created_at = models.DateTimeField("答题时间", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "答题记录"
        verbose_name_plural = "答题记录"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[OK] {self.question}" if self.is_correct else f"[NO] {self.question}"

class QuestionNote(models.Model):
    """题目问答/笔记"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="notes")
    content = models.TextField("问答内容")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "题目笔记"
        verbose_name_plural = "题目笔记"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[NOTE] {self.question}"
