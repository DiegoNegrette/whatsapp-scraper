from datetime import timedelta

# import ipdb
import traceback

from celery.utils.log import get_task_logger
from django.utils import timezone

from selenium.common.exceptions import StaleElementReferenceException

from service.celery import app
from ..models import Appointment, ProjectConfiguration
from ..scraper.whatsappcom.whatsapp import WhatsappSiteScraper

queue_name = "scraping_queue"
logger = get_task_logger("scraper")


ES_MESSAGE = """Hola {}, un recordatorio de tu cita con Samuel Higgs en Advanced Quiropráctica el {} at {}. Nos vemos 😊

Saludos cordiales

El equipo de AQ
📍C/Trafalgar 4, 10-A
"""

EN_MESSAGE = """Hi {}, a reminder your appointment with Samuel Higgs at Advanced Quiropráctica is on {} at {}. See you there :)

Warmest,

AQ Team
📍C/Trafalgar 4, 10-A
"""

GET_BASE_MESSAGE = {"en": EN_MESSAGE, "es": ES_MESSAGE}


@app.task(queue=queue_name)
def open_whatsapp():
    task_name = "open_whatsapp"
    scraper = WhatsappSiteScraper(task_identifier=task_name)
    try:
        scraper.init_driver()
        scraper.bootstrap_account()
        scraper.navigate_to(scraper.base_url)
        MAX_ATTEMPTS = 5
        current_attempt = 1
        while not scraper.is_logged_in() and current_attempt <= MAX_ATTEMPTS:
            scraper.sleep(5)
            current_attempt += 1
        scraper.sleep(30)
    except KeyboardInterrupt:
        stacktrace = "KeyboardInterrupt"
    except Exception as e:
        # ipdb.set_trace()
        stacktrace = traceback.format_exc()
        scraper.log(stacktrace)
        scraper.log("{} Terminating".format(e))

    scraper.close_driver()


@app.task(queue=queue_name)
def send_whatsapp_remainder():
    now = timezone.now()

    project_config = ProjectConfiguration.get_solo()

    target_appointments = {
        "for_first_notification": [],
        "for_second_notification": [],
    }

    if project_config.enable_first_notification:
        start_of_tomorrow = now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        hours_before_first_notification = timedelta(hours=24)

        # Now calculate the time window for sending notifications.
        # We need to check if the appointment `starts_at` is before today's time minus `hours_before_first_notification`.
        # That means, for appointments tomorrow, we calculate `starts_at - hours_before_first_notification` and compare it to `now`.

        appointments_to_notify = Appointment.objects.filter(
            starts_at__gte=start_of_tomorrow,  # Appointment is tomorrow or later
            starts_at__lt=start_of_tomorrow
            + timedelta(
                days=1
            ),  # Appointment is tomorrow (starts at least midnight and less than 24 hours)
            first_notification_sent_at__isnull=True,  # First notification hasn't been sent yet
            patient_phone_number__isnull=False,  # Patient has a phone number
        ).exclude(status="cancelled")

        # Filter out appointments where the `starts_at - hours_before_first_notification` is before now
        appointments_to_notify_for_the_first_time = appointments_to_notify.filter(
            starts_at__lt=now
            + hours_before_first_notification  # The appointment is within the notification window (starts_at - hours_before_first_notification <= now)
        ).values_list("id", flat=True)
        target_appointments["for_first_notification"] = list(
            appointments_to_notify_for_the_first_time
        )

    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = start_of_today + timedelta(
        days=1
    )  # End of today (midnight to midnight)

    # Calculate the time window for the second notification
    hours_before_second_notification = timedelta(
        hours=project_config.hours_before_second_notification
    )

    # Filter appointments:
    appointments_to_notify = Appointment.objects.filter(
        starts_at__gte=start_of_today,  # Appointments starting today or later
        starts_at__lt=end_of_today,  # Appointments starting before midnight today
        second_notification_sent_at__isnull=True,  # Second notification hasn't been sent yet
        patient_phone_number__isnull=False,  # Patient has a phone number
    ).exclude(status="cancelled")

    # Further filter by time window for the second notification (starts_at - hours_before_second_notification should be before now)
    appointments_to_notify = appointments_to_notify.filter(
        starts_at__lt=now
        + hours_before_second_notification  # The appointment should be within the notification window (starts_at - hours_before_second_notification <= now)
    ).values_list("id", flat=True)

    target_appointments["for_second_notification"] = list(appointments_to_notify)
    if len(target_appointments["for_first_notification"]) or len(
        target_appointments["for_second_notification"]
    ):
        execute_send_whatsapp_remainder.apply_async(args=[target_appointments])


@app.task(bind=True, queue=queue_name)
def execute_send_whatsapp_remainder(self, target_appointments):
    appoinments_ids = (
        target_appointments["for_first_notification"]
        + target_appointments["for_second_notification"]
    )
    appointments = Appointment.objects.filter(id__in=appoinments_ids).order_by(
        "starts_at"
    )
    task_name = "send_whatsapp_remainder"
    project_config = ProjectConfiguration.get_solo()
    scraper = WhatsappSiteScraper(task_identifier=task_name)
    try:
        scraper.init_driver()
        scraper.login()
        for appointment in appointments:
            notification_result = None
            try:
                scraper.start_a_new_chat(
                    user_name=project_config.name_of_the_default_whatsapp_user
                )
                # scraper.send_message(appointment.patient_phone_number)
                scraper.send_message("+584121800402")
                scraper.open_conversation_with_last_number()
                max_attempts = 3
                current_attempt = 1
                while current_attempt <= max_attempts:
                    scraper.log(
                        f"Attempt ({current_attempt}) to send the message for {appointment.patient_name} on {appointment.patient_phone_number}"
                    )
                    try:
                        BASE_MESSAGE = GET_BASE_MESSAGE[appointment.language or "en"]
                        scraper.send_message(
                            BASE_MESSAGE.format(
                                appointment.patient_name.split(" ")[0],
                                appointment.starts_at.date(),
                                appointment.starts_at.time().strftime("%H:%M"),
                                appointment.patient_name,
                                appointment.starts_at.date(),
                                appointment.starts_at.time().strftime("%H:%M"),
                            )
                        )
                        scraper.sleep(2)
                        notification_result = Appointment.NOTIFICATION_RESULT_SUCCESS
                        break
                    except StaleElementReferenceException:
                        pass
                    current_attempt += 1
                if not notification_result:
                    notification_result = Appointment.NOTIFICATION_RESULT_ERROR
            except Exception as e:
                notification_result = Appointment.NOTIFICATION_RESULT_ERROR
                stacktrace = traceback.format_exc()
                scraper.log(stacktrace)
                scraper.log("{} Going to next message".format(e))
            if appointment.id in target_appointments["for_first_notification"]:
                appointment.mark_first_notification_sent(notification_result)
            if appointment.id in target_appointments["for_second_notification"]:
                appointment.mark_second_notification_sent(notification_result)
    except KeyboardInterrupt:
        stacktrace = "KeyboardInterrupt"
    except Exception as e:
        # ipdb.set_trace()
        stacktrace = traceback.format_exc()
        scraper.log(stacktrace)
        scraper.log("{} Terminating".format(e))
        # Retry the task if an exception occurs
        raise self.retry(exc=e, countdown=60, max_retries=3)
    finally:
        scraper.close_driver()
