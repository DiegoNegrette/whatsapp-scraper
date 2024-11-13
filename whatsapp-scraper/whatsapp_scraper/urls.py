from django.urls import path
from .views import AppointmentListView, health_check, TriggerTaskView

urlpatterns = [
    path("", AppointmentListView.as_view(), name="appointment_list"),
    path("trigger-task/", TriggerTaskView.as_view(), name="trigger_task"),
    path("health/", health_check, name="health_check"),
]
