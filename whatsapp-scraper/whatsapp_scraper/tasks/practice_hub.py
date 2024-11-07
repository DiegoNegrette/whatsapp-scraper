from dateutil.relativedelta import relativedelta

from celery.utils.log import get_task_logger
from django.db.models import Q
from django.utils import timezone

from ..models import Appointment
from ..utils import convert_datetime_str_to_aware
from service.celery import app
from third_party.practice_hub.api import PracticeHubAPI

logger = get_task_logger("practice_hub")
queue_name = "practice_hub_queue"

practice_hub = PracticeHubAPI()


@app.task(queue=queue_name)
def sync_appointments():
    logger.info("Starting sync appointment")
    appointments = practice_hub.get_todays_appointments()
    id_to_appointment_dict = {
        appointment["id"]: appointment for appointment in appointments
    }

    appointments_practice_hub_ids = id_to_appointment_dict.keys()

    logger.info(
        f"Found {len(appointments_practice_hub_ids)} task{'s' if len(appointments_practice_hub_ids) > 1 else ''}"
    )

    existing_appointments = Appointment.objects.filter(
        id__in=appointments_practice_hub_ids
    )
    practice_hub_id_to_existing_appointment_obj_dict = {
        appointment.practice_hub_id: appointment
        for appointment in existing_appointments
    }

    appointments_to_create = []
    appointments_to_update = []
    for idx, practice_hub_id in enumerate(appointments_practice_hub_ids):
        appointment_new_data = id_to_appointment_dict[practice_hub_id]
        appointment_date_spain = convert_datetime_str_to_aware(
            appointment_new_data["start"], "%Y-%m-%d %H:%M:%S"
        )
        if practice_hub_id in practice_hub_id_to_existing_appointment_obj_dict:
            existing_appointment = practice_hub_id_to_existing_appointment_obj_dict[
                practice_hub_id
            ]

            existing_appointment.starts_at = appointment_date_spain
            existing_appointment.status = appointment_new_data["status"]
            appointments_to_update.append(existing_appointment)
            logger.info(
                f"{idx + 1} Updated appointment for {existing_appointment.patient_name} at {existing_appointment.starts_at}"  # noqa
            )
        else:
            # Create appointment
            appointment_dict = {
                "practice_hub_id": appointment_new_data["id"],
                "patient_id": appointment_new_data["patient_id"],
                "patient_name": appointment_new_data["patient_name"],
                "patient_phone_number": None,
                "starts_at": appointment_date_spain,
                "status": appointment_new_data["status"],
            }
            new_appointment = Appointment(**appointment_dict)
            appointments_to_create.append(new_appointment)
            logger.info(
                f"{idx + 1} Creating appointment for {new_appointment.patient_name} at {new_appointment.starts_at}"
            )

    Appointment.objects.bulk_update(appointments_to_update, ["starts_at", "status"])
    Appointment.objects.bulk_create(appointments_to_create)
    logger.info("Finished sync appointment")


@app.task(queue=queue_name)
def sync_missing_phone_numbers():
    logger.info("Starting missing phone number sync")
    target_appointments = Appointment.objects.filter(
        Q(start__gt=timezone.now()), Q(patient_phone_number__isnull=True)
    )
    patients = practice_hub.get_patients()
    patient_id_to_patient_info_dict = {patient["id"]: patient for patient in patients}
    appointments_to_update = []
    for appointment in target_appointments:
        pattient_info = patient_id_to_patient_info_dict.get(appointment.patient_id)
        selected_phone_number = None
        if pattient_info and len(pattient_info["numbers"]) > 1:
            for phone_info in pattient_info["numbers"]:
                if phone_info["country_code"] and phone_info["number"]:
                    selected_phone_number = f"+{phone_info['country_code']}{phone_info['number'].replace(' ', '')}"
                    break
        if selected_phone_number:
            appointment.patient_phone_number = selected_phone_number
            appointments_to_update.append(appointment)
            logger.info(
                f"Updated missing phone number for appointment {appointment.id}"
            )
    Appointment.objects.bulk_update(appointments_to_update, ["patient_phone_number"])
    logger.info("Finished missing phone number sync")


@app.task(queue=queue_name)
def delete_older_appointments():
    one_month_ago = timezone.now() - relativedelta(months=1)
    Appointment.objects.filter(created__lt=one_month_ago).delete()
