from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.http import FileResponse, HttpResponse
import json
from .forms import (
    RescheduleForm
)
# ============ Reschedule Views ============

@login_required
def reschedule(request, appointment_id):
    """Reschedule an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    doctor = appointment.doctor
    time_slots = DoctorTimeSlot.objects.filter(doctor=doctor)
    
    if request.method == 'POST':
        new_date = request.POST.get('appointment_date')
        new_time_id = request.POST.get('appointment_time')
        
        try:
            new_time_slot = DoctorTimeSlot.objects.get(id=new_time_id, doctor=doctor)
        except DoctorTimeSlot.DoesNotExist:
            messages.error(request, "Time slot not found.")
            return redirect('appointments:reschedule', appointment_id=appointment_id)
        
        new_selected_date = timezone.datetime.strptime(new_date, '%Y-%m-%d').date()
        today = timezone.now().date()
        
        if new_selected_date < today:
            messages.error(request, "Please select an upcoming date.")
            return redirect('appointments:reschedule', appointment_id=appointment_id)
        
        appointment.appointment_date = new_date
        appointment.doctor_time_slot = new_time_slot
        appointment.status = 'rescheduled'
        appointment.save()
        
        messages.success(request, "Appointment rescheduled successfully.")
        return redirect('accounts:user_profile')
    
    return render(request, 'appointments/reschedule.html', {
        'appointment': appointment,
        'doctor': doctor,
        'time_slots': time_slots
    })


@login_required
def alternatives(request, appointment_id):
    """Show alternative time slots"""
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    doctor = appointment.doctor
    
    alternative_slots = DoctorTimeSlot.objects.filter(doctor=doctor).exclude(
        id=appointment.doctor_time_slot.id
    )
    
    return render(request, 'appointments/alternatives.html', {
        'appointment': appointment,
        'doctor': doctor,
        'alternative_slots': alternative_slots
    })


@login_required
def confirm_reschedule(request):
    """Confirm rescheduling"""
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        time_slot_id = request.POST.get('time_slot_id')
        appointment_date = request.POST.get('appointment_date')
        
        appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
        time_slot = get_object_or_404(DoctorTimeSlot, id=time_slot_id)
        
        appointment.appointment_date = appointment_date
        appointment.doctor_time_slot = time_slot
        appointment.status = 'rescheduled'
        appointment.save()
        
        messages.success(request, "Appointment successfully rescheduled.")
        return redirect('accounts:user_profile')


# ============ Medicine Views ============

@login_required
def add_medicine(request):
    """Add a new medicine (Doctor only)"""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "You are not registered as a doctor.")
        return redirect('appointments:appointment')
    
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicine added successfully.")
            return redirect('appointments:add_medicine')
    else:
        form = MedicineForm()
    
    # Get all medicines
    medicines = Medicine.objects.all()
    
    return render(request, 'appointments/add_medicine.html', {
        'form': form,
        'medicines': medicines
    })


@login_required
def edit_medicine(request, medicine_id):
    """Edit a medicine (Doctor only)"""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "You are not registered as a doctor.")
        return redirect('appointments:appointment')
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicine updated successfully.")
            return redirect('appointments:add_medicine')
    else:
        form = MedicineForm(instance=medicine)
    
    return render(request, 'appointments/edit_medicine.html', {
        'form': form,
        'medicine': medicine
    })


@login_required
def delete_medicine(request, medicine_id):
    """Delete a medicine"""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "You are not registered as a doctor.")
        return redirect('appointments:appointment')
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    medicine.delete()
    messages.success(request, "Medicine deleted successfully.")
    return redirect('appointments:add_medicine')


