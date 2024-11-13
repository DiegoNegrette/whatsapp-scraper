from django.db import migrations
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule
from django.utils.timezone import now


def create_periodic_tasks(apps, schema_editor):
    # Task 1: delete_older_appointments (runs daily at 00:00)
    if not PeriodicTask.objects.filter(name="delete_older_appointments").exists():
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="0",
        )
        PeriodicTask.objects.create(
            crontab=schedule,
            name="delete_older_appointments",
            task="whatsapp_scraper.tasks.practice_hub.delete_older_appointments",
            start_time=now(),
        )

    # Task 2: send_notification (runs every Monday at 8am)
    if not PeriodicTask.objects.filter(
        name="send_weekly_appointment_metrics_email"
    ).exists():
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="8",
            day_of_week="1",  # Monday
        )
        PeriodicTask.objects.create(
            crontab=schedule,
            name="send_notifications",
            task="whatsapp_scraper.tasks.notifications.send_weekly_appointment_metrics_email",
            start_time=now(),
        )

    # Task 3: send_whatsapp_remainder (runs every hour)
    if not PeriodicTask.objects.filter(name="send_whatsapp_remainder").exists():
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.HOURS,
        )
        PeriodicTask.objects.create(
            interval=schedule,
            name="send_whatsapp_remainder",
            task="whatsapp_scraper.tasks.whatsapp.send_whatsapp_remainder",
            start_time=now(),
        )

    # Task 4: sync_appointments (runs every 2 hours from 10am to 9pm)
    if not PeriodicTask.objects.filter(name="sync_appointments").exists():
        for hour in range(10, 21, 2):  # 10am, 12pm, 2pm...9pm
            schedule, created = CrontabSchedule.objects.get_or_create(
                minute="0",
                hour=str(hour),
            )
            PeriodicTask.objects.create(
                crontab=schedule,
                name=f"sync_appointments_{hour}",
                task="whatsapp_scraper.tasks.practice_hub.sync_appointments",
                start_time=now(),
            )

    # Task 5: sync_missing_phone_numbers (runs every 2 hours from 11am to 10pm)
    if not PeriodicTask.objects.filter(name="sync_missing_phone_numbers").exists():
        for hour in range(11, 23, 2):  # 11am, 1pm, 3pm...10pm
            schedule, created = CrontabSchedule.objects.get_or_create(
                minute="0",
                hour=str(hour),
            )
            PeriodicTask.objects.create(
                crontab=schedule,
                name=f"sync_missing_phone_numbers_{hour}",
                task="whatsapp_scraper.tasks.practice_hub.sync_missing_phone_numbers",
                start_time=now(),
            )


class Migration(migrations.Migration):

    dependencies = [
        (
            "django_celery_beat",
            "0001_initial",
        ),  # Adjust this to your django_celery_beat migration dependency
        (
            "whatsapp_scraper",
            "0001_initial",
        ),  # Adjust based on your app's previous migration
    ]

    operations = [
        migrations.RunPython(create_periodic_tasks),
    ]
