
from datetime import datetime, timedelta
from django.utils import timezone
from .models import DoctorTimeSlot, Appointment


def get_available_time_slots(doctor, appointment_date):
    """
    Get all available slots for a doctor on a specific date
    """
    day_of_week = appointment_date.weekday()
    
    # Find all time slots for that day
    time_slots = DoctorTimeSlot.objects.filter(
        doctor=doctor,
        day_of_week=day_of_week
    )
    
    available_slots = []
    
    for slot in time_slots:
        # Check if slot is already booked
        booked_count = Appointment.objects.filter(
            doctor=doctor,
            doctor_time_slot=slot,
            appointment_date=appointment_date
        ).count()
        
        # If slots available
        if booked_count < 5:  # Max 5 appointments per slot
            available_slots.append({
                'id': slot.id,
                'start_time': slot.start_time,
                'end_time': slot.end_time,
                'available': 5 - booked_count
            })
    
    return available_slots


def check_doctor_availability(doctor, appointment_date):
    """
    Check if doctor is available on a specific date
    """
    day_of_week = appointment_date.weekday()
    
    has_slots = DoctorTimeSlot.objects.filter(
        doctor=doctor,
        day_of_week=day_of_week
    ).exists()
    
    return has_slots


def suggest_alternative_dates(doctor, original_date, days_ahead=60):
    """
    Suggest alternative dates in next 60 days
    """
    alternatives = []
    current_date = original_date + timedelta(days=1)
    end_date = original_date + timedelta(days=days_ahead)
    
    while current_date <= end_date and len(alternatives) < 10:
        day_of_week = current_date.weekday()
        
        # Check if available slots exist for this day
        slots = DoctorTimeSlot.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week
        )
        
        if slots.exists():
            for slot in slots:
                booked_count = Appointment.objects.filter(
                    doctor=doctor,
                    doctor_time_slot=slot,
                    appointment_date=current_date
                ).count()
                
                if booked_count < 5:
                    alternatives.append({
                        'date': current_date,
                        'time': f"{slot.start_time} - {slot.end_time}",
                        'slot_id': slot.id
                    })
                    break  # One slot is enough
        
        current_date += timedelta(days=1)
    
    return alternatives


def calculate_serial_number(doctor):
    """
    Get today's serial number for a doctor
    """
    today = timezone.now().date()
    
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).count()
    
    return today_appointments + 1


def get_patient_medicine_schedule(patient, date=None):
    """
    Get patient's medicine schedule for a specific date
    """
    if date is None:
        date = timezone.now().date()
    
    from .models import Prescription
    
    # Get all prescriptions created before this date
    prescriptions = Prescription.objects.filter(
        patient=patient,
        appointment__appointment_date__lte=date
    )
    
    all_medicines = []
    for prescription in prescriptions:
        for medicine in prescription.medicines:
            all_medicines.append({
                'name': medicine.get('name'),
                'dosage': medicine.get('dosage'),
                'frequency': medicine.get('frequency'),
                'duration': medicine.get('duration'),
                'doctor': prescription.doctor.name
            })
    
    return all_medicines


def validate_appointment_date(date, doctor=None):
    """
    Validate if appointment date is valid
    """
    today = timezone.now().date()
    
    # Must be future date
    if date <= today:
        return False, "Please select a future date"
    
    # If doctor specified, check availability
    if doctor:
        has_slots = check_doctor_availability(doctor, date)
        if not has_slots:
            return False, "Doctor not available on this date"
    
    return True, "Date is valid"
