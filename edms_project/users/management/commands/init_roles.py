from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Создание групп пользователей'

    def handle(self, *args, **kwargs):
        roles = ['Администратор', 'Секретарь', 'Сотрудник', 'Руководитель']
        for role in roles:
            Group.objects.get_or_create(name=role)
        self.stdout.write(self.style.SUCCESS("Группы успешно созданы."))
