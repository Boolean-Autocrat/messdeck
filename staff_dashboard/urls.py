from django.urls import path
from .views import (
    dashboard_view,
    complaints_feedback_view,
    delete_complaint_view,
    calculate_fees,
    export_fees,
)

urlpatterns = [
    path("dashboard/", dashboard_view, name="staffdashboard"),
    path("dashboard/complaints/", complaints_feedback_view, name="staffcomplaints"),
    path(
        "dashboard/complaints/delete/",
        delete_complaint_view,
        name="deletestaffcomplaint",
    ),
    path("dashboard/calculate-fees/", calculate_fees, name="calculate_fees"),
    path("dashboard/export-bills/", export_fees, name="export_bills"),
]
