from django.contrib.auth.models import User
from django.core.management import BaseCommand

from app.models import Question, Profile, Tag, Answer


class Command(BaseCommand):
    help = 'Fills the database'

    def handle(self, *args, **options):
        print("Очистка ответов...")
        Answer.objects.all().delete()
        print("Очистка вопросов...")
        Question.objects.all().delete()
        print("Очистка тегов...")
        Tag.objects.all().delete()
        print("Очистка профилей...")
        Profile.objects.all().delete()
        print("Очистка юзеров...")
        User.objects.all().delete()
        print("Очистка завершена успешно...")