from __future__ import annotations

import json
from datetime import timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Appointment, Doctor, Patient


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("clinic:dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("clinic:login")


@login_required
def dashboard_view(request):
    seven_days_ago = timezone.now() - timedelta(days=7)

    daily_appointments = (
        Appointment.objects.filter(date_time__gte=seven_days_ago)
        .annotate(date=TruncDate("date_time"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    dates = [obj["date"].strftime("%d.%m.%Y") for obj in daily_appointments]
    counts = [obj["count"] for obj in daily_appointments]

    total_patients = Patient.objects.count()
    pending_appointments = Appointment.objects.filter(status="pending").count()

    by_status = (
        Appointment.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )
    status_counts = {obj["status"]: obj["count"] for obj in by_status}

    context = {
        "dates_json": json.dumps(dates, ensure_ascii=False),
        "counts_json": json.dumps(counts, ensure_ascii=False),
        "status_counts_json": json.dumps(
            [
                status_counts.get("pending", 0),
                status_counts.get("completed", 0),
                status_counts.get("cancelled", 0),
            ],
            ensure_ascii=False,
        ),
        "total_patients": total_patients,
        "pending_appointments": pending_appointments,
    }
    return render(request, "dashboard.html", context)


@login_required
def appointment_list_view(request):
    appointments = Appointment.objects.select_related("patient", "doctor", "doctor__user").order_by("-date_time")

    status_filter = request.GET.get("status")
    doctor_filter = request.GET.get("doctor_id")

    if status_filter:
        appointments = appointments.filter(status=status_filter)
    if doctor_filter:
        appointments = appointments.filter(doctor_id=doctor_filter)

    doctors = Doctor.objects.select_related("user").all()

    context = {
        "appointments": appointments,
        "doctors": doctors,
        "status_filter": status_filter or "",
        "doctor_filter": doctor_filter or "",
    }
    return render(request, "appointment_list.html", context)


@login_required
def appointment_create_view(request):
    if request.method == "POST":
        iin = (request.POST.get("iin") or "").strip()
        full_name = (request.POST.get("full_name") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        doctor_id = request.POST.get("doctor_id")
        date_time = request.POST.get("date_time")
        notes = (request.POST.get("notes") or "").strip()

        patient, _created = Patient.objects.get_or_create(
            iin=iin,
            defaults={"full_name": full_name, "phone": phone},
        )

        # Если пациент уже был, но пользователь ввёл новые данные — обновим.
        changed = False
        if full_name and patient.full_name != full_name:
            patient.full_name = full_name
            changed = True
        if phone and patient.phone != phone:
            patient.phone = phone
            changed = True
        if changed:
            patient.save(update_fields=["full_name", "phone"])

        Appointment.objects.create(
            patient=patient,
            doctor_id=doctor_id,
            date_time=date_time,
            notes=notes,
        )
        return redirect("clinic:appointment_list")

    doctors = Doctor.objects.select_related("user").all()
    return render(request, "appointment_create.html", {"doctors": doctors})
