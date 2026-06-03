"""Models: quiz domain"""
import re
import os
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class QuestionType(models.Model):
    id = models.AutoField(primary_key=True)
    question_type = models.CharField(max_length=20)
    tihao = models.CharField(max_length=20)
    question = models.TextField()  # 修改为TextField
    options = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=20)

class JskjgQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    question_type = models.CharField(max_length=20)
    tihao = models.CharField(max_length=20)
    question = models.TextField()  # 修改为TextField
    options = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=20)

class WxpzxQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    question_type = models.CharField(max_length=20)
    tihao = models.CharField(max_length=20)
    question = models.TextField()  # 修改为TextField
    options = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=20)

class UserAnswer(models.Model):

    ti_type = models.CharField(max_length=20)
    tihao = models.CharField(max_length=20)
    date = models.DateField()
    ident = models.CharField(max_length=20)

    # def __str__(self):
    #     return self.UserAnswer

class Tihao(models.Model):
    题号=models.TextField(blank=False, null=False)

