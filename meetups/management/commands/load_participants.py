import random
from datetime import datetime, timedelta, time

from django.core.management.base import BaseCommand
from faker import Faker

from meetups.models import Visitor, Event, Section


class Command(BaseCommand):

    help = 'Скрипт загружает количество участников.' \
           'Передайте число участников аргументом в виде python manage.py load_participants <количество>'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help=u'Количество создаваемых пользователей')

    def load_participants(self, total):

        min_year = 1900
        max_year = datetime.now().year

        start = datetime(min_year, 1, 1, 00, 00, 00)
        years = max_year - min_year + 1
        end = start + timedelta(days=365 * years)

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
                is_speaker=bool(random.getrandbits(1)),
            )
        for _ in range(3):
            Event.objects.update_or_create(
                title=fake.sentence(nb_words=2),
                start_date = start + (end - start) * random.random(),
                description = fake.paragraph(nb_sentences=5),
                is_closed = False,
            )

        for speaker in Visitor.objects.filter(is_speaker=True):
            Section.objects.update_or_create(
                event=random.choice(list(Event.objects.all())),
                #speaker = ,
                title = fake.sentence(nb_words=3),

                start_time = time(hour=random.randint(8, 15),
                                    minute=random.randint(0, 59),
                                    second=random.randint(0, 59)
                ),
                end_time = time(hour=random.randint(8, 15),
                                    minute=random.randint(0, 59),
                                    second=random.randint(0, 59)
                ),
                description = fake.paragraph(nb_sentences=5),
            )


    def handle(self, *args, **kwargs):
        total = kwargs['total']
        self.load_participants(total)
