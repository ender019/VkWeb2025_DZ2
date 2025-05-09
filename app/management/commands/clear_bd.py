from datetime import datetime

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from app.models import Question, Profile, Tag, Answer, QuestionsTags, QuestionsLikes, AnswersLikes


class Command(BaseCommand):
    help = 'Fills the database'

    def handle(self, *args, **options):
        st_time = datetime.now()
        print(st_time.now()-st_time, "Очистка промежуточных таблиц...")
        QuestionsTags.objects.all().delete()
        QuestionsLikes.objects.all().delete()
        AnswersLikes.objects.all().delete()

        print(st_time.now()-st_time, "Очистка ответов...")
        Answer.objects.all().delete()
        print(st_time.now()-st_time, "Очистка вопросов...")
        Question.objects.all().delete()
        print(st_time.now()-st_time, "Очистка тегов...")
        Tag.objects.all().delete()
        print(st_time.now()-st_time, "Очистка профилей...")
        Profile.objects.all().delete()
        print(st_time.now()-st_time, "Очистка юзеров...")
        User.objects.all().delete()
        print(st_time.now()-st_time, "Завершено!")