"""Models: quiz domain"""
import re
import os
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class Question(models.Model):
    category = models.CharField(max_length=10, verbose_name="题库类别", help_text="爆破/井工/危装")
    question_type = models.CharField(max_length=20, verbose_name="题型")
    tihao = models.CharField(max_length=20, verbose_name="题号")
    question = models.TextField(verbose_name="题目")
    options = models.CharField(max_length=200, verbose_name="选项")
    correct_answer = models.CharField(max_length=20, verbose_name="正确答案")
    analysis = models.TextField(verbose_name="解析", blank=True, default="")

    class Meta:
        db_table = "app01_question"
        verbose_name = "题库"

class UserAnswer(models.Model):

    ti_type = models.CharField(max_length=20)
    tihao = models.CharField(max_length=20)
    date = models.DateField()
    ident = models.CharField(max_length=20)
