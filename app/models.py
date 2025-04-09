from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

from app.model_manager import ProfileManager, QuestionManager, AnswerManager, TagManager


# Create your models here.
class Profile(models.Model):
    objects = ProfileManager()

    nickname = models.CharField(max_length=50)
    avatar = models.CharField(max_length=254, null=True, default=None)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'profiles'


class Tag(models.Model):
    objects = TagManager()

    title = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'tags'


class Question(models.Model):
    objects = QuestionManager()

    title = models.CharField(max_length=100, unique=True)
    text = models.TextField(null=False)
    posted = models.DateTimeField()

    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='qst_creator')

    class Meta:
        db_table = 'questions'


class Answer(models.Model):
    objects = AnswerManager()

    text = models.TextField(null=False)
    correct = models.BooleanField(default=False)
    posted = models.DateTimeField(auto_now_add=True)

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='ans_creator')

    class Meta:
        db_table = 'answers'


class QuestionsLikes(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='qst_likes')

    class Meta:
        db_table = 'questions_likes'
        unique_together = (('profile', 'question'),)


class AnswersLikes(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='ans_likes')

    class Meta:
        db_table = 'answers_likes'
        unique_together = (('profile', 'answer'),)


class QuestionsTags(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='tagged_questions')

    class Meta:
        db_table = 'questions_tags'
        unique_together = (('question', 'tag'),)