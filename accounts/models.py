from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    address = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    gender = models.CharField(max_length=10, choices=GENDER)

    def __str__(self):
        full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        return full_name or self.user.username
