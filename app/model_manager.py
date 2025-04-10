from django.db import models
from django.db.models import Count, Sum, Q


class ProfileManager(models.Manager):
    def get_most_active(self, kol: int = 8):
        return (self.annotate(quest_kol=models.Count("qst_creator")).order_by('-quest_kol')
                    .values_list("nickname", flat=True)[:kol])


class QuestionManager(models.Manager):
    def full_listing(self, page):
        return (self.filter(id__in=page.object_list.values_list('id', flat=True)).annotate(
                like=Count("likes", filter=Q(likes__pos__exact=1)),
                dis=Count("likes", filter=Q(likes__pos__exact=0))
            ).order_by("-posted").all())

    def full_hot(self, page):
        return (self.filter(id__in=page.object_list.values_list('id', flat=True)).annotate(
                like=Count("likes", filter=Q(likes__pos__exact=1)),
                dis=Count("likes", filter=Q(likes__pos__exact=0)),
                ans_kol=models.Count("answer")
            ).order_by('-ans_kol', "-posted").all())

    def get_listing(self):
        return self.order_by("-posted").all()

    def get_hot(self):
        return self.annotate(ans_kol=models.Count("answer")).order_by('-ans_kol', "-posted").all()

    def get_by_id(self, question_id):
        return (self.annotate(like=Sum('likes__pos'), dis=Count("likes", filter=Q(likes__pos__exact=0)))
                .get(pk=question_id))

    def get_by_tag(self, title):
        return self.filter(tags__tag__title=title).order_by('-posted').all()

    def get_liked_question(self):
        return self.order_by('-likes_kol', "-posted").all()


class AnswerManager(models.Manager):
    def get_correct(self, question_id: int):
        return self.filter(question_id=question_id, correct=True).all()

    def full_answers(self, page):
        return (self.filter(id__in=page.object_list.values_list('id', flat=True)).annotate(
                like=Count("likes", filter=Q(likes__pos__exact=1)),
                dis=Count("likes", filter=Q(likes__pos__exact=0))
            ).order_by("-like", "-posted").all())

    def get_by_question_id(self, question_id):
        return (self.filter(question_id=question_id).annotate(likes_kol=models.Sum("likes__pos"))
                .order_by('-likes_kol').all())


class TagManager(models.Manager):
    def get_id_by_title(self, title: str):
        return self.filter(title=title).first()

    def get_popular_tags(self):
        return (self.annotate(quest_kol=models.Count("tagged_questions"))
                .order_by('-quest_kol').values_list("title", flat=True)[:20])