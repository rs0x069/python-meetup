import json
import os

import django
from .models import User
from faker import Faker


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()


def main():
    fake = Faker("ru_RU")
    for _ in range(50):
        User.objects.update_or_create(
            firstname=fake.name_female(),
            lastname=fake.lastname_female(),
            email=fake.email(),
            profession=fake.job(),
            company=fake.company(),
            tel=fake.phone_number(),
            telegram_id=f'@{fake.user_name()}',
            info=fake.paragraph(nb_sentences=5),

        )


if __name__ == '__main__':
    main()