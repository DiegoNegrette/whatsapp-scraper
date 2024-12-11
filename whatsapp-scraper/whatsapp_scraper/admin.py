from django.contrib import admin

from solo.admin import SingletonModelAdmin

from .models import Appointment, ProjectConfiguration


admin.site.register(ProjectConfiguration, SingletonModelAdmin)


# Register your models here.
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "practice_hub_id",
        "patient_id",
        "patient_name",
        "patient_phone_number",
        "starts_at",
        "status",
        "first_notification_sent_at",
        "first_notification_result",
        "second_notification_sent_at",
        "second_notification_result",
        "created",
        "modified",
    )
