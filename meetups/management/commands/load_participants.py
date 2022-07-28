import os

import django
from django.core.management.base import BaseCommand
from faker import Faker

from meetups.models import Visitor


class Command(BaseCommand):

    help = 'Скрипт загружает количество участников.' \
           'Передайте число участников аргументом в виде python manage.py load_participants <количество>'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help=u'Количество создаваемых пользователей')

    def load_participants(self, total):
        fake = Faker("ru_RU")
        for _ in range(total):
            Visitor.objects.update_or_create(
                firstname=fake.first_name_female(),
                lastname=fake.last_name_female(),
                email=fake.email(),
                position=fake.job(),
                company=fake.company(),
                phone_number=fake.phone_number(),
                telegram_id=f'@{fake.user_name()}',
                about_oneself=fake.paragraph(nb_sentences=5),
            )

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        self.load_participants(total)
