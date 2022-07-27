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
            name=fake.name(),
            country=fake.country(),
            city=fake.city(),
            profession=fake.job(),
            company=fake.company(),
            tel=fake.phone_number(),
            telegram_id=f'@{fake.user_name()}'
        )


if __name__ == '__main__':
    main()