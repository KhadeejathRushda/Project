from django.urls import path
from .views import (
    upload_xray,
    doctor_dashboard,
    patient_reports,
    verify_report,
    download_report_pdf
)

urlpatterns = [
    path('upload-xray/', upload_xray, name='upload-xray'),
    path('doctor-dashboard/', doctor_dashboard, name='doctor-dashboard'),
    path('patient-reports/<int:patient_id>/', patient_reports, name='patient-reports'),
    path('verify-report/<int:report_id>/', verify_report, name='verify-report'),
    path('download-report/<int:report_id>/', download_report_pdf, name='download-report-pdf'),
]