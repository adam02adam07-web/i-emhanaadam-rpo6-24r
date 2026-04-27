from __future__ import annotations

import json
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from clinic.models import Appointment, Doctor, Patient


class Command(BaseCommand):
    help = "Импортирует тестовые данные из JSON файла"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Путь к JSON файлу")

    def handle(self, *args, **kwargs):
        json_file = kwargs["json_file"]

        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f"Файл {json_file} не найден!"))
            return

        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Импорт пациентов
        for p_data in data.get("patients", []):
            Patient.objects.get_or_create(
                iin=p_data["iin"],
                defaults={"full_name": p_data["full_name"], "phone": p_data["phone"]},
            )

        # Импорт врачей (+ создание user с хешированием пароля)
        for d_data in data.get("doctors", []):
            user, created = User.objects.get_or_create(username=d_data["username"])
            if created:
                user.set_password(d_data["password"])
                user.first_name = d_data.get("first_name", "")
                user.last_name = d_data.get("last_name", "")
                user.save()

            Doctor.objects.get_or_create(user=user, defaults={"specialty": d_data["specialty"]})

        # Импорт приемов
        for a_data in data.get("appointments", []):
            try:
                patient = Patient.objects.get(iin=a_data["patient_iin"])
                doctor = Doctor.objects.get(user__username=a_data["doctor_username"])

                dt = parse_datetime(a_data["date_time"])
                if dt is None:
                    raise ValueError(f"Неверная дата date_time: {a_data['date_time']}")

                Appointment.objects.get_or_create(
                    patient=patient,
                    doctor=doctor,
                    date_time=dt,
                    defaults={"status": a_data.get("status", "pending"), "notes": a_data.get("notes", "")},
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Ошибка привязки: {e}"))

        self.stdout.write(self.style.SUCCESS("Импорт успешно завершен!"))
