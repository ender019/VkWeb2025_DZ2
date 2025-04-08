from datetime import timedelta, datetime

from django.core.management import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from app.models import Question, Profile, Answer, Tag
from random import randint, choices


class Command(BaseCommand):
    help = 'Fills the database'
    img = ["PELMEN.png", "frog.webp", "volk.jpg", "bird.jpg"]

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Kol')

    def rand_str(self, kol=10) -> str:
        let = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return "".join(let[randint(0, 51)] for i in range(kol))
    
    def rand_date(self) -> datetime:
        return datetime.now()-timedelta(seconds=randint(1, 10**9))

    @transaction.atomic
    def handle(self, *args, **options):
        kol: int = options['ratio']

        tags = [Tag(id=i, title=f"tag{i}") for i in range(kol)]
        users = [User(
                username=self.rand_str(randint(10,50)),
                email=self.rand_str(randint(5,20))+"@mail.ru"
            ) for i in range(kol)]
        profiles = [Profile(
            nickname=self.rand_str(randint(10,50)),
            avatar=f"/img/{choices(self.img)[0]}",
            user=users[i]
        ) for i in range(kol)]
        questions = [Question(
                title=f"Question {i}",
                text="question "*randint(1, 100),
                posted=self.rand_date(),
                profile=profiles[randint(0, kol-1)]
            ) for i in range(kol*10)]
        answers = [Answer(
                text="answer "*randint(1, 10)+str(i),
                correct=randint(0, 1),
                posted=self.rand_date(),
                question=questions[randint(0, 10*kol-1)],
                profile=profiles[randint(0, kol-1)]
            ) for i in range(kol*100)]

        Tag.objects.bulk_create(tags)
        User.objects.bulk_create(users)
        Profile.objects.bulk_create(profiles)
        Question.objects.bulk_create(questions)
        Answer.objects.bulk_create(answers)

        for q in questions:
            q.tags.set(choices(tags, k=randint(1, kol)))
            q.likes.set(choices(profiles, k=randint(0, kol)))
        for a in answers:
            a.likes.set(choices(profiles, k=randint(0, kol)))
