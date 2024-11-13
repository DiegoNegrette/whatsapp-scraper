from django.db import models
from django.utils import timezone
from model_utils.models import TimeStampedModel
from solo.models import SingletonModel


class ProjectConfiguration(SingletonModel):
    enable_first_notification = models.BooleanField(
        default=True,
        verbose_name="Enable first notification 24 prior to the appointment",
    )

    hours_before_second_notification = models.IntegerField(
        default=3,
        verbose_name="Hours before second appointment notification in the same day",
    )

    name_of_the_default_whatsapp_user = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Name of the default whatsapp user used by the scraper to send phone numbers",
    )

    class Meta:
        verbose_name = "Project configuration"
        verbose_name_plural = "Project configurations"

    def __str__(self):
        return "Project configuration"


class ModifiedTimeStampMixin(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if "update_fields" in kwargs:
            kwargs["update_fields"] = list(
                set(list(kwargs["update_fields"]) + ["modified"])
            )
        return super(ModifiedTimeStampMixin, self).save(*args, **kwargs)


class Appointment(ModifiedTimeStampMixin, TimeStampedModel):
    NOTIFICATION_RESULT_SUCCESS = "success"
    NOTIFICATION_RESULT_ERROR = "error"

    CH_NOTIFICATION_RESULT = (
        (NOTIFICATION_RESULT_SUCCESS, NOTIFICATION_RESULT_SUCCESS),
        (NOTIFICATION_RESULT_ERROR, NOTIFICATION_RESULT_ERROR),
    )

    practice_hub_id = models.IntegerField(null=False, blank=False)
    patient_id = models.IntegerField(null=False, blank=False)
    patient_name = models.CharField(max_length=500, null=False, blank=False)
    patient_phone_number = models.CharField(max_length=100, null=True, blank=True)
    starts_at = models.DateTimeField(null=False, blank=False)
    status = models.CharField(max_length=255, null=True, blank=True)
    first_notification_sent_at = models.DateTimeField(null=True, blank=True)
    first_notification_result = models.CharField(
        max_length=255, choices=CH_NOTIFICATION_RESULT, null=True, blank=True
    )
    second_notification_sent_at = models.DateTimeField(null=True, blank=True)
    second_notification_result = models.CharField(
        max_length=255, choices=CH_NOTIFICATION_RESULT, null=True, blank=True
    )

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"

    def __str__(self):
        return f"{self.patient_name} ({self.patient_phone_number}) at {self.starts_at}"

    def mark_first_notification_sent(self, result):
        self.first_notification_sent_at = timezone.now()
        self.first_notification_result = result
        self.save(
            update_fields=["first_notification_sent_at", "first_notification_result"]
        )

    def mark_second_notification_sent(self, result):
        self.second_notification_sent_at = timezone.now()
        self.second_notification_result = result
        self.save(
            update_fields=["second_notification_sent_at", "second_notification_result"]
        )
