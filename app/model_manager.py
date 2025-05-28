from django.db import models
from django.db.models import Count, Q, Case, When, IntegerField


class ProfileManager(models.Manager):
    def get_most_active(self, kol: int = 8):
        return (self.annotate(quest_kol=models.Count("qst_creator")).order_by('-quest_kol')
                    .values_list("nickname", flat=True)[:kol])

    def get_current (self, username):
        try:
            return self.get(user__username=username)
        except Exception as e:
            return None

    def updating(self, username, data):
        profile = self.get_current(username)
        if data.get("username"): profile.user.username = data.get("username")
        if data.get("email"): profile.user.email = data.get("email")
        if data.get("nickname"): profile.nickname = data.get("nickname")
        if data.get("avatar"): profile.avatar = data.get("avatar")
        profile.user.save()
        profile.save()

class QuestionManager(models.Manager):
    def full_listing(self, page, profile_id: int = -1):
        return (self.filter(id__in=page.object_list.values_list('id', flat=True)).annotate(
                like=Count("likes", filter=Q(likes__pos=1)),
                dis=Count("likes", filter=Q(likes__pos=0)),
                fase=Case(
                    When(
                        Q(likes__pos=1, likes__profile_id=profile_id),
                        then=2
                    ), When(
                        Q(likes__pos=0, likes__profile_id=profile_id),
                        then=1
                    ),
                    default=0,
                    output_field=IntegerField()
                ),
            ).order_by("-posted").all())

    def full_hot(self, page, profile_id: int = -1):
        return (self.filter(id__in=page.object_list.values_list('id', flat=True)).annotate(
                like=Count("likes", filter=Q(likes__pos=1)),
                dis=Count("likes", filter=Q(likes__pos=0)),
                fase=Case(
                    When(
                        Q(likes__pos=1, likes__profile_id=profile_id),
                        then=2
                    ), When(
                        Q(likes__pos=0, likes__profile_id=profile_id),
                        then=1
                    ),
                    default=0,
                    output_field=IntegerField()
                ),
                ans_kol=models.Count("answer")
            ).order_by('-ans_kol', "-posted").all())

    def get_listing(self):
        return self.order_by("-posted").all()

    def get_hot(self):
        return self.annotate(ans_kol=models.Count("answer")).order_by('-ans_kol', "-posted").all()

    def get_by_id(self, question_id, profile_id: int = -1):
        return (self.annotate(
                    like=Count("likes", filter=Q(likes__pos=1)),
                    dis=Count("likes", filter=Q(likes__pos=0)),
                    fase=Case(
                        When(
                            Q(likes__pos=1, likes__profile_id=profile_id),
                            then=2
                        ), When(
                            Q(likes__pos=0, likes__profile_id=profile_id),
                            then=1
                        ),
                        default=0,
                        output_field=IntegerField()
                    ),
                ).get(pk=question_id))

    def get_by_tag(self, title):
        return self.filter(tags__tag__title=title).order_by('-posted').all()

    def get_liked_question(self):
        return self.order_by('-likes_kol', "-posted").all()


class AnswerManager(models.Manager):
    def get_correct(self, question_id: int):
        return self.filter(question_id=question_id, correct=True).all()

    def set_correct(self, answer_id: int, cor: bool):
        return self.filter(id=answer_id).update(correct=cor)

    def full_answers(self, page, profile_id: int = -1):
        return (self.filter(id__in=page.object_list.values_list('id', flat=True)).annotate(
                like=Count("likes", filter=Q(likes__pos=1)),
                dis=Count("likes", filter=Q(likes__pos=0)),
                fase=Case(
                    When(
                        Q(likes__pos=1, likes__profile_id=profile_id),
                        then=2
                    ), When(
                        Q(likes__pos=0, likes__profile_id=profile_id),
                        then=1
                    ),
                    default=0,
                    output_field=IntegerField()
                ),
            ).order_by("-like", "-posted").all())

    def get_by_question_id(self, question_id):
        return (self.filter(question_id=question_id)
                .annotate(likes_kol=models.Count("likes", filter=Q(likes__pos=1)))
                .order_by('-likes_kol', "-posted").all())


class TagManager(models.Manager):
    def get_id_by_title(self, title: str):
        return self.filter(title=title).first()

    def get_popular_tags(self):
        return (self.annotate(quest_kol=models.Count("tagged_questions"))
                .order_by('-quest_kol').values_list("title", flat=True)[:20])


class QuestionsLikesManager(models.Manager):
    def get_count(self, question_id: int):
        res =self.filter(question_id=question_id).aggregate(
                like=Count("id", filter=Q(pos=1)),
                dis=Count("id", filter=Q(pos=0))
            )
        return res

    def add_react(self, profile_id: int, question_id: int, pos: int):
        print(profile_id, question_id, pos)
        obj = self.filter(profile_id=profile_id, question_id=question_id).first()
        if not obj:
            self.create(profile_id=profile_id, question_id=question_id, pos=pos)
            return pos + 1
        if obj.pos == pos:
            obj.delete()
            return 0
        else:
            obj.pos = pos
            obj.save(update_fields=['pos'])
            return pos + 1


class AnswersLikesManager(models.Manager):
    def get_count(self, answer_id: int):
        return self.filter(answer_id=answer_id).aggregate(
                like=Count("id", filter=Q(pos=1)),
                dis=Count("id", filter=Q(pos=0))
            )

    def add_react(self, profile_id: int, answer_id: int, pos: int):
        obj = self.filter(profile_id=profile_id, answer_id=answer_id).first()
        if not obj:
            self.create(profile_id=profile_id, answer_id=answer_id, pos=pos)
            return pos + 1
        if obj.pos == pos:
            obj.delete()
            return 0
        else:
            obj.pos = pos
            obj.save(update_fields=['pos'])
            return pos + 1