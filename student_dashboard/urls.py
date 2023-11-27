from django.urls import path
from .views import dashboard_view, feedback_view, mark_attendance

urlpatterns = [
    path("dashboard/", dashboard_view, name="studentdashboard"),
    path("feedback/", feedback_view, name="studentfeedback"),
    path("mark_attendance/", mark_attendance, name="mark_attendance"),
]
