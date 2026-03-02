import os

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from blacklist.models import Reasons
from blacklist.enums import initial_black_reasons

class Command(BaseCommand):
    help = 'Заполнение таблиц первичными данными'
    def handle(self, *args, **options):
        Users = get_user_model()
        print('Проверка суперпользователя...', end='')

        su_username = os.environ.get('SUPERUSER_USERNAME')
        su_email = os.environ.get('SUPERUSER_EMAIL')
        su_passwd = os.environ.get('SUPERUSER_PASSWORD')

        if not su_username or not su_email or not su_passwd:
            print('Не заданы параметры суперпользователя, пропуск хода')
            usr = (None, None)
        else:
            usr = Users.objects.get_or_create(
                username=su_username,
                email=su_email,
                defaults={'password': make_password(su_passwd),
                          "first_name": os.environ.get('SUPERUSER_FIRST_NAME'),
                          "last_name": os.environ.get('SUPERUSER_LAST_NAME'),
                          "is_staff": True,
                          "is_superuser": True
                          })
        if usr[1]:
            print('Суперпользователь добавлен')
        else:
            print('Суперпользователь существует')
        
        print('Заполнение справочника причин блокировки...', end='')
        reason_count = [0,0]
        for item in initial_black_reasons:

            rsn, created = Reasons.objects.get_or_create(
                reason_description=item)

            if created:
                reason_count[0] += 1
            else:
                reason_count[1] += 1
        
        print(f"Добавлено {reason_count[0]} причин, а также {reason_count[1]} причин уже существуют")
        

        print('Скрипт закончил работу')