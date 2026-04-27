from __future__ import annotations

import random

from django.core.management.base import BaseCommand

from clinic.models import Patient


FIRST_NAMES = [
    "Азамат",
    "Айгерим",
    "Данияр",
    "Жанар",
    "Арман",
    "Мадина",
    "Нурсултан",
    "Аружан",
    "Ерасыл",
    "Алина",
    "Тимур",
    "Айша",
    "Руслан",
    "Диана",
    "Ильяс",
    "Гульнур",
    "Санжар",
    "Сауле",
    "Нияз",
    "Еркебулан",
]

LAST_NAMES = [
    "Ахметов",
    "Оспанова",
    "Серикбаев",
    "Касымова",
    "Ермеков",
    "Тлеубаева",
    "Садыков",
    "Бекжанова",
    "Турсынов",
    "Калиева",
    "Абдрахманов",
    "Нурмуханбетова",
    "Кожахметов",
    "Омарова",
    "Мусин",
    "Смагулова",
    "Исмаилов",
    "Жумабаева",
    "Сапаров",
    "Нурланов",
]

MIDDLE_NAMES = [
    "Алиевич",
    "Серикович",
    "Ерланович",
    "Нурланович",
    "Талгатович",
    "Канатович",
    "Жандосович",
    "Болатович",
    "Рустемович",
    "Саматович",
    "Ермекович",
    "Аскарович",
    "Рамазанович",
]


class Command(BaseCommand):
    help = "Генерирует большое количество тестовых пациентов"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=1000, help="Сколько пациентов создать")

    def handle(self, *args, **kwargs):
        count = kwargs["count"]
        created = 0
        skipped = 0

        # Берем текущий максимум иина из наших тестовых данных, чтобы не пересекаться.
        next_iin_num = 800000000000

        for _ in range(count):
            # Простой уникальный 12-значный ИИН для тестовой среды.
            while True:
                next_iin_num += 1
                iin = str(next_iin_num)
                if not Patient.objects.filter(iin=iin).exists():
                    break

            full_name = f"{random.choice(LAST_NAMES)} {random.choice(FIRST_NAMES)} {random.choice(MIDDLE_NAMES)}"
            phone = f"+7 70{random.randint(0, 9)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"

            _, was_created = Patient.objects.get_or_create(
                iin=iin,
                defaults={"full_name": full_name, "phone": phone},
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово. Создано пациентов: {created}. Пропущено (дубли): {skipped}."
            )
        )
