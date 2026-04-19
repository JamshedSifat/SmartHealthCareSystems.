from django.contrib import admin
from .models import Doctor, DoctorTimeSlot, Appointment, Hospital, Blood

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'cost', 'available_spots', 'status']
    list_filter = ['specialty', 'status']
    search_fields = ['name', 'specialty']


@admin.register(DoctorTimeSlot)
class DoctorTimeSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'start_time', 'end_time']
    list_filter = ['doctor']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'doctor', 'appointment_date', 'created_at']
    list_filter = ['appointment_date', 'doctor']
    search_fields = ['user__username', 'doctor__name']
@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['hospital_name', 'location', 'capacity']
    search_fields = ['hospital_name', 'location']


@admin.register(Blood)
class BloodAdmin(admin.ModelAdmin):
    list_display = ['blood_group', 'quantity', 'expiry_date']
    list_filter = ['blood_group', 'expiry_date']
