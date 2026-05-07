from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # ============ Appointment URLs ============
    path('', views.appointment, name='appointment'),
    path('search/', views.doctor_search, name='doctor_search'),
    path('create/<int:doctor_id>/', views.create_appointment, name='create_appointment'),
    path('cancel/<int:appointment_id>/<int:doctor_id>/', views.cancel_appointment, name='cancel_appointment'),
    
    # ============ Doctor & Reviews URLs ============
    path('doctor/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('doctor/<int:doctor_id>/review/', views.create_review, name='create_review'),
    path('doctor/<int:doctor_id>/review/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('top-doctors/', views.top_doctors, name='top_doctors'),
    
    # ============ Reschedule URLs ============
    path('appointment/<int:appointment_id>/reschedule/', views.reschedule, name='reschedule'),
    path('appointment/<int:appointment_id>/alternatives/', views.alternatives, name='alternatives'),
    path('confirm-reschedule/', views.confirm_reschedule, name='confirm_reschedule'),
    
    # ============ Medicine URLs ============
    path('medicine/add/', views.add_medicine, name='add_medicine'),
    path('medicine/<int:medicine_id>/edit/', views.edit_medicine, name='edit_medicine'),
    path('medicine/<int:medicine_id>/delete/', views.delete_medicine, name='delete_medicine'),
    
    # ============ Prescription URLs ============
    path('prescription/upload/<int:appointment_id>/', views.upload_prescription, name='upload_prescription'),
    path('prescription/edit/<int:prescription_id>/', views.edit_prescription, name='edit_prescription'),
    path('prescriptions/', views.prescription_history, name='prescription_history'),
    path('prescription/<int:prescription_id>/', views.view_prescription, name='view_prescription'),
    path('prescription/<int:prescription_id>/download-pdf/', views.download_prescription_pdf, name='download_prescription_pdf'),
    path('prescriptions/doctor/', views.doctor_prescriptions_list, name='doctor_prescriptions_list'),
    path('medicine-reminder/', views.medicine_reminder, name='medicine_reminder'),
    
    # ============ Doctor Appointments ============
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    
    # ============ Emergency URLs ============
    path('emergency/', views.emergency, name='emergency'),
    path('blood-search/', views.blood_search, name='blood_search'),
]
