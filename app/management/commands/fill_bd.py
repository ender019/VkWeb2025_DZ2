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
    batch = 10**6
    likers_kol = 400

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

    def handle(self, *args, **options):
        kol: int = options['ratio']
        likers_kol = min(kol, self.likers_kol)
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

        print(st_time.now()-st_time, "Генерация связей тегов...")
        ind = 0
        puck = []
        for q in questions:
            puck.extend([QuestionsTags(question=q, tag=t) for t in sample(tags, k=randint(1, 5))])
            ind += 1
            if len(puck) >= self.batch:
                QuestionsTags.objects.bulk_create(puck, batch_size=len(puck))
                puck = []
                print(f"{st_time.now() - st_time}     Готово {ind} записей из {kol*10}")
        if len(puck) > 0:
            QuestionsTags.objects.bulk_create(puck, batch_size=len(puck))
            print(f"{st_time.now() - st_time}     Готово {ind} записей из {kol * 10}")

        print(st_time.now()-st_time, "Генерация связей вопросов...")
        ind = 0
        puck = []
        for p in profiles:
            puck.extend([
                QuestionsLikes(question=q, profile=p, pos=randint(0, 1))
                for q in sample(questions, k=randint(0, self.likers_kol))
            ])
            ind += 1
            if len(puck) >= self.batch:
                QuestionsLikes.objects.bulk_create(puck, batch_size=len(puck))
                puck = []
                print(f"{st_time.now() - st_time}     Готово {ind} записей из {kol}")
        if len(puck) > 0:
            QuestionsLikes.objects.bulk_create(puck, batch_size=len(puck))
            print(f"{st_time.now() - st_time}     Готово {ind} записей из {kol}")

        print(st_time.now()-st_time, "Генерация связей ответов...")
        ind = 0
        puck = []
        for p in profiles:
            puck.extend([
                AnswersLikes(answer=a, profile=p, pos=randint(0, 1))
                for a in sample(answers, k=randint(0, self.likers_kol))
            ])
            ind += 1
            if len(puck) >= self.batch:
                AnswersLikes.objects.bulk_create(puck, batch_size=len(puck))
                puck = []
                print(f"{st_time.now() - st_time}     Готово {ind} записей из {kol}")
        if len(puck) > 0:
            AnswersLikes.objects.bulk_create(puck, batch_size=len(puck))
            print(f"{st_time.now() - st_time}     Готово {ind} записей из {kol}")

        print(st_time.now()-st_time, "Выполнено!")