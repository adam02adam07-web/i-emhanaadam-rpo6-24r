from django.contrib import admin

from .models import Appointment, Doctor, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "iin", "phone", "created_at")
    search_fields = ("iin", "full_name", "phone")
    ordering = ("-created_at",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("user", "specialty")
    search_fields = ("user__username", "user__first_name", "user__last_name", "specialty")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("date_time", "patient", "doctor", "status")
    list_filter = ("status", "doctor")
    search_fields = ("patient__iin", "patient__full_name", "doctor__specialty", "doctor__user__username")
    ordering = ("-date_time",)
