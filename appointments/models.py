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
      
