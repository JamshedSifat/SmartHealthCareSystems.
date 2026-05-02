from django.db import models
from django.contrib.auth.models import User
from datetime import time


class Medicine(models.Model):
    FREQUENCY_CHOICES = [
        ('once', 'Once Daily'),
        ('twice', 'Twice Daily'),
        ('thrice', 'Three Times Daily'),
        ('four', 'Four Times Daily'),
    ]

    DOSAGE_UNIT_CHOICES = [
        ('tablet', 'Tablet(s)'),
        ('capsule', 'Capsule(s)'),
        ('ml', 'ML'),
        ('mg', 'MG'),
        ('drops', 'Drop(s)'),
        ('teaspoon', 'Teaspoon(s)'),
        ('tablespoon', 'Tablespoon(s)'),
    ]

    FOOD_TIMING_CHOICES = [
        ('any', 'No Preference'),
        ('before', 'Before Food'),
        ('after', 'After Food'),
        ('with', 'With Food'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    dosage_amount = models.DecimalField(max_digits=6, decimal_places=2)
    dosage_unit = models.CharField(max_length=20, choices=DOSAGE_UNIT_CHOICES, default='tablet')
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='once')
    food_timing = models.CharField(max_length=10, choices=FOOD_TIMING_CHOICES, default='any')
    start_date = models.DateField()
    end_date = models.DateField()
    instructions = models.TextField(blank=True)
    doctor_name = models.CharField(max_length=200, blank=True)
    prescription_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.dosage_amount} {self.dosage_unit}"

    class Meta:
        ordering = ['-created_at']


class ReminderTime(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='reminder_times')
    time = models.TimeField()

    def __str__(self):
        return f"{self.medicine.name} at {self.time.strftime('%I:%M %p')}"

    class Meta:
        ordering = ['time']


class DoseTaken(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    reminder_time = models.ForeignKey(ReminderTime, on_delete=models.CASCADE)
    date_taken = models.DateField()
    time_taken = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine.name} taken on {self.date_taken}"

    class Meta:
        unique_together = ('medicine', 'reminder_time', 'date_taken')
        ordering = ['-date_taken', '-time_taken']
