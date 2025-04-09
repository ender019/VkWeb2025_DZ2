from datetime import timedelta, datetime

from django.core.management import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from app.models import Question, Profile, Answer, Tag, QuestionsLikes, AnswersLikes, QuestionsTags
from random import randint, choices, sample


class Command(BaseCommand):
    help = 'Fills the database'
    img = ["PELMEN.png", "frog.webp", "volk.jpg", "bird.jpg"]

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Kol')

    def rand_str(self, kol=10) -> str:
        let = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return "".join(let[randint(0, 51)] for i in range(kol))
    
    def rand_date(self) -> datetime:
        return timezone.make_aware(
            datetime.now()-timedelta(seconds=randint(1, 10**9)),
            timezone=timezone.get_current_timezone()
        )

    @transaction.atomic
    def handle(self, *args, **options):
        kol: int = options['ratio']

        print("генерация тегов...")
        tags = [Tag(id=i, title=f"tag{i}") for i in range(kol)]
        print("генерация юзеров...")
        users = [User(
                username=self.rand_str(randint(10,50)),
                email=self.rand_str(randint(5,20))+"@mail.ru"
            ) for i in range(kol)]
        print("генерация профилей...")
        profiles = [Profile(
            nickname=self.rand_str(randint(10,50)),
            avatar=f"/img/{choices(self.img)[0]}",
            user=users[i]
        ) for i in range(kol)]
        print("генерация вопросов...")
        questions = [Question(
                title=f"Question {i}",
                text="question "*randint(1, 100),
                posted=self.rand_date(),
                profile=profiles[randint(0, kol-1)]
            ) for i in range(kol*10)]
        print("генерация ответов...")
        answers = [Answer(
                text="answer "*randint(1, 10)+str(i),
                correct=randint(0, 1),
                posted=self.rand_date(),
                question=questions[randint(0, 10*kol-1)],
                profile=profiles[randint(0, kol-1)]
            ) for i in range(kol*100)]

        print("запись объектов...")
        Tag.objects.bulk_create(tags)
        User.objects.bulk_create(users)
        Profile.objects.bulk_create(profiles)
        Question.objects.bulk_create(questions)
        Answer.objects.bulk_create(answers)

        print("генерация связей тегов...")
        QuestionsTags.objects.bulk_create([
            QuestionsTags(question=q, tag=t)
            for q in questions
            for t in sample(tags, k=randint(1, kol))
        ])
        print("генерация связей вопросов...")
        QuestionsLikes.objects.bulk_create([
            QuestionsLikes(question=q, profile=p)
            for q in questions
            for p in sample(profiles, k=randint(0, kol))
        ])
        print("генерация связей ответов...")
        AnswersLikes.objects.bulk_create([
            AnswersLikes(answer=a, profile=p)
            for a in answers
            for p in sample(profiles, k=randint(0, kol))
        ])