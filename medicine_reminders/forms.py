
from django import forms
from .models import Medicine, ReminderTime


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name',
            'dosage_amount',
            'dosage_unit',
            'frequency',
            'food_timing',
            'start_date',
            'end_date',
            'doctor_name',
            'prescription_date',
            'instructions'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg',
                'placeholder': 'Medicine name'
            }),
            'dosage_amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg',
                'step': '0.5'
            }),
            'dosage_unit': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg'
            }),
            'frequency': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg'
            }),
            'food_timing': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg',
                'type': 'date'
            }),
            'doctor_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg',
                'placeholder': 'Doctor name'
            }),
            'prescription_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg',
                'type': 'date'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg resize-none',
                'rows': 3,
                'placeholder': 'Special instructions'
            }),
        }


class ReminderTimeForm(forms.ModelForm):
    class Meta:
        model = ReminderTime
        fields = ['time']
        widgets = {
            'time': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg',
                'type': 'time'
            }),
        }
