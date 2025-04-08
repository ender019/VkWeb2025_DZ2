from django.db import models
from django.db.models import Count


class ProfileManager(models.Manager):
    def get_most_active(self, kol: int = 8):
        return (self.annotate(quest_kol=models.Count("question")).order_by('-quest_kol')
                    .values_list("nickname", flat=True)[:kol])

    def get_by_id(self, id: int):
        return self.select_related("user").get(pk=id)


class QuestionManager(models.Manager):
    def get_listing(self):
        return self.prefetch_related("tags", "profile").order_by("-posted").annotate(likes_kol=Count("likes")).all()

    def get_hot(self):
        return self.get_listing().annotate(ans_kol=models.Count("answer")).order_by('-ans_kol').all()

    def get_by_tag(self, title):
        return self.get_listing().filter(tags__title=title).all()

    def get_liked_question(self):
        return self.get_listing().order_by('-likes_kol').all()


class AnswerManager(models.Manager):
    def get_correct_answer(self, question_id: int):
        return self.filter(question_id=question_id, correct=True).all()

    def get_liked_answer(self):
        return self.prefetch_related("profile").annotate(likes_kol=models.Count("likes")).order_by('-likes_kol').all()


class TagManager(models.Manager):
    def get_id_by_title(self, title: str):
        return self.filter(title=title).first()

    def get_popular_tags(self):
        return self.annotate(quest_kol=models.Count("question")).order_by('-quest_kol').values_list("title", flat=True)