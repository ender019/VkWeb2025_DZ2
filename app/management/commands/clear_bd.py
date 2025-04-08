from django.contrib.auth.models import User
from django.core.management import BaseCommand

from app.models import Question, Profile, Tag, Answer


class Command(BaseCommand):
    help = 'Fills the database'

    def handle(self, *args, **options):
        Answer.objects.all().delete()
        Question.objects.all().delete()
        Tag.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.all().delete()