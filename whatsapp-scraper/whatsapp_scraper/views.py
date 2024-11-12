from django.utils import timezone
from django.views.generic import ListView
from .models import Appointment
from .forms import DateFilterForm
from datetime import timedelta

from django.http import JsonResponse
from django.views import View
from django.conf import settings

from .tasks import open_whatsapp


# Create the task view
class TriggerTaskView(View):
    def post(self, request, *args, **kwargs):
        # Trigger the background task or any logic you want to handle
        try:
            open_whatsapp.delay()

            # Respond with success message
            return JsonResponse({"message": "Open whatsapp trigerred successfully!"})

        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)


class AppointmentListView(ListView):
    model = Appointment
    template_name = "appointments/appointment_list.html"
    context_object_name = "appointments"

    def get_queryset(self):
        filter_date = self.request.GET.get("date", timezone.now().date())
        if isinstance(filter_date, str):
            filter_date = timezone.datetime.strptime(filter_date, "%Y-%m-%d").date()

        start_of_day = timezone.make_aware(
            timezone.datetime.combine(filter_date, timezone.datetime.min.time())
        )
        end_of_day = start_of_day + timedelta(days=1)

        return Appointment.objects.filter(
            starts_at__gte=start_of_day,
            starts_at__lt=end_of_day,
        ).order_by("starts_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = DateFilterForm(self.request.GET or None)

        # Calculate metrics
        total_appointments = context["appointments"].count()
        first_notification_count = (
            context["appointments"]
            .filter(first_notification_sent_at__isnull=False)
            .count()
        )
        second_notification_count = (
            context["appointments"]
            .filter(second_notification_sent_at__isnull=False)
            .count()
        )

        # Pass the metrics to the context
        context["total_appointments"] = total_appointments
        context["first_notification_count"] = first_notification_count
        context["second_notification_count"] = second_notification_count

        # Retrieve the VNC URL from settings
        context["vnc_url"] = (
            settings.VNC_URL
        )  # Ensure this setting exists in your settings.py

        return context
