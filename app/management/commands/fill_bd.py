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
    batch = 1000

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Kol')

    def rand_str(self, kol=10) -> str:
        let = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return "".join(choices(let, k=kol))
    
    def rand_date(self) -> datetime:
        return timezone.make_aware(
            datetime.now()-timedelta(seconds=randint(1, 10**9)),
            timezone=timezone.get_current_timezone()
        )

    @transaction.atomic
    def handle(self, *args, **options):
        kol: int = options['ratio']
        st_time = datetime.now()

        print(st_time.now()-st_time, "генерация тегов...")
        tags = [Tag(id=i, title=f"tag{i}") for i in range(kol)]
        print(st_time.now()-st_time, "генерация юзеров...")
        users = [User(
                username=self.rand_str(randint(10,50)),
                email=self.rand_str(randint(5,20))+"@mail.ru"
            ) for i in range(kol)]
        print(st_time.now()-st_time, "генерация профилей...")
        profiles = [Profile(
            nickname=self.rand_str(randint(10,50)),
            avatar=f"/img/{choices(self.img)[0]}",
            user=users[i]
        ) for i in range(kol)]
        print(st_time.now()-st_time, "генерация вопросов...")
        questions = [Question(
                title=f"Question {i}",
                text="question "*randint(1, 100),
                posted=self.rand_date(),
                profile=profiles[randint(0, kol-1)]
            ) for i in range(kol*10)]
        print(st_time.now()-st_time, "генерация ответов...")
        answers = [Answer(
                text="answer "*randint(1, 10)+str(i),
                correct=randint(0, 1),
                posted=self.rand_date(),
                question=questions[randint(0, 10*kol-1)],
                profile=profiles[randint(0, kol-1)]
            ) for i in range(kol*100)]

        print(st_time.now()-st_time, "запись объектов...")
        Tag.objects.bulk_create(tags)
        User.objects.bulk_create(users)
        Profile.objects.bulk_create(profiles)
        Question.objects.bulk_create(questions)
        Answer.objects.bulk_create(answers)

        print(st_time.now()-st_time, "генерация связей тегов...")
        ind = 0
        while ind < kol*10:
            QuestionsTags.objects.bulk_create([
                QuestionsTags(question=questions[i], tag=t)
                for i in range(ind, min(ind + self.batch, kol*10))
                for t in sample(tags, k=randint(1, 20))
            ])
            ind += self.batch
            print(f"    Готово {ind} записей из {kol*10}")
        print(st_time.now()-st_time, "генерация связей вопросов...")
        ind = 0
        while ind < kol*10:
            QuestionsLikes.objects.bulk_create([
                QuestionsLikes(question=questions[i], profile=p)
                for i in range(ind, min(ind + self.batch, kol*10))
                for p in sample(profiles, k=randint(0, kol))
            ])
            ind += self.batch
            print(f"    Готово {ind} записей из {kol*10}")
        print(st_time.now()-st_time, "генерация связей ответов...")
        ind = 0
        while ind < kol*100:
            AnswersLikes.objects.bulk_create([
                AnswersLikes(answer=answers[i], profile=p)
                for i in range(ind, min(ind + self.batch, kol * 100))
                for p in sample(profiles, k=randint(0, kol))
            ])
            ind += self.batch
            print(f"    Готово {ind} записей из {kol*10}")