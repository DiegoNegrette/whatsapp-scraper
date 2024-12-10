from datetime import timedelta
import math

from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string  # For rendering HTML templates
from django.utils import timezone

from service.celery import app
from ..models import Appointment

queue_name = "scraping_queue"
logger = get_task_logger("scraper")


@app.task(queue=queue_name)
def send_weekly_appointment_metrics_email():
    # Calculate the start and end of the previous week
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday() + 7)
    end_of_week = start_of_week + timedelta(days=6)

    # Query the appointments for the past week
    appointments = Appointment.objects.filter(
        starts_at__range=[start_of_week, end_of_week]
    )

    # Collect details for each appointment
    appointment_data = []
    first_notification_count = 0
    second_notification_count = 0
    total_appointments = appointments.count()

    for appointment in appointments:
        # Collect patient details and notification information
        appointment_data.append(
            {
                "patient_name": appointment.patient_name,
                "appointment_date": appointment.starts_at,
                "first_notification_sent_at": appointment.first_notification_sent_at,
                "first_notification_result": appointment.first_notification_result,
                "second_notification_sent_at": appointment.second_notification_sent_at,
                "second_notification_result": appointment.second_notification_result,
            }
        )

        # Count the notifications sent
        if appointment.first_notification_sent_at:
            first_notification_count += 1
        if appointment.second_notification_sent_at:
            second_notification_count += 1

    # Calculate notification success rates
    first_notification_rate = math.floor(
        (first_notification_count / total_appointments) * 100
        if total_appointments > 0
        else 0
    )
    second_notification_rate = math.floor(
        (second_notification_count / total_appointments) * 100
        if total_appointments > 0
        else 0
    )

    # Prepare the email content using HTML
    subject = "Weekly Appointment Metrics"
    context = {
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "appointment_data": appointment_data,
        "first_notification_rate": first_notification_rate,
        "second_notification_rate": second_notification_rate,
        "total_appointments": total_appointments,
    }

    # Use Django's template rendering to generate the HTML email
    message = render_to_string("emails/weekly_appointment_metrics.html", context)

    # Send the email
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # Replace with your sender email
        ["d.negrette42@gmail.com"],  # Replace with target email
        fail_silently=False,
        html_message=message,  # Send as HTML
    )
