import csv

from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка данных из csv файла.'

    def handle(self, *args, **kwargs):
        with open(
            'data/ingredients.csv', encoding='utf-8',
        ) as file:
            reader = csv.reader(file)
            for ingridients in reader:
                Ingredient.objects.get_or_create(**ingridients)
        self.stdout.write(self.style.SUCCESS('Все данные загружены.'))
