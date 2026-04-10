from django.db import models
from django.contrib.auth.models import User
class Doctor(models.Model):
    image = models.ImageField()
    name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    cost = models.IntegerField()
    available_spots = models.PositiveIntegerField()
    next_available_appointment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
class DoctorTimeSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.doctor.name} ({self.start_time} - {self.end_time})"

class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    doctor_time_slot = models.ForeignKey(DoctorTimeSlot, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
    appointment_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    serial_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username
