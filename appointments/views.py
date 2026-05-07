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
# ============ Appointment Views ============

def appointment(request):
    """Display all doctors"""
    doctors = Doctor.objects.all()
    total_doctors = doctors.count()
    
    return render(request, "appointments/appointment.html", {
        'doctors': doctors,
        'total_doctors': total_doctors,
        'search_query': ''
    })


def doctor_search(request):
    """Search for doctors"""
    query_d = request.GET.get('q', '')

    if query_d:
        words = query_d.split()
        doctors = Doctor.objects.none()

        for word in words:
            if word.lower() == "available":
                doctors = doctors | Doctor.objects.filter(status=True)
            elif word.lower() == "unavailable":
                doctors = doctors | Doctor.objects.filter(status=False)
            else:
                doctors = doctors | Doctor.objects.filter(
                    name__icontains=word
                ) | Doctor.objects.filter(
                    specialty__icontains=word
                )
    else:
        messages.error(request, "Search bar was empty")
        return redirect('appointments:appointment')

    if not doctors:
        messages.error(request, "No doctors found.")
        return redirect('appointments:appointment')

    return render(request, 'appointments/appointment.html', {
        'doctors': doctors,
        'search_query': query_d,
        'total_doctors': doctors.count()
    })


@login_required
def create_appointment(request, doctor_id):
    """Create an appointment"""
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        description = request.POST.get('description')
        appointment_time_id = request.POST.get('appointment_time')
        
        try:
            time_slot = DoctorTimeSlot.objects.get(id=appointment_time_id, doctor=doctor)
        except DoctorTimeSlot.DoesNotExist:
            messages.error(request, "Time slot not found.")
            return redirect(reverse('appointments:create_appointment', args=[doctor_id]))
        
        selected_date = timezone.datetime.strptime(appointment_date, '%Y-%m-%d').date()
        today = timezone.now().date()

        if not doctor.status:
            doctor.available_spots = doctor.available_spots + 1
            doctor.status = True
            doctor.save()
            if selected_date < doctor.next_available_appointment_date:
                messages.error(request, f"Choose a date after: {doctor.next_available_appointment_date.strftime('%d/%B/%Y')}")
                return redirect(reverse('appointments:create_appointment', args=[doctor_id]))
        else:
            if selected_date < today:
                messages.error(request, "Please select an upcoming date.")
                return redirect(reverse('appointments:create_appointment', args=[doctor_id]))

        serial_number = Appointment.objects.filter(doctor=doctor, appointment_date=selected_date).count() + 1

        appointment = Appointment(
            user=request.user,
            doctor=doctor,
            appointment_date=appointment_date,
            description=description,
            doctor_time_slot=time_slot,
            serial_number=serial_number
        )
        appointment.save()

        doctor.available_spots -= 1
        if doctor.available_spots == 0:
            doctor.status = False
        doctor.save()

        messages.success(request, "Appointment successfully booked")
        return redirect(reverse('appointments:appointment'))

    return render(request, 'appointments/create_appointment.html', {'doctor': doctor})


def cancel_appointment(request, appointment_id, doctor_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if appointment.user == request.user:
        doctor.available_spots += 1
        doctor.save()
        appointment.delete()
        messages.success(request, "Appointment cancelled successfully.")
    else:
        messages.error(request, "You are not authorized to cancel this appointment.")

    return redirect('accounts:user_profile')

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

# ============ Doctor Profile & Reviews Views ============

def doctor_detail(request, doctor_id):
    """Display doctor profile details"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    reviews = DoctorReview.objects.filter(doctor=doctor)
    time_slots = DoctorTimeSlot.objects.filter(doctor=doctor)
    
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    return render(request, 'appointments/doctor_detail.html', {
        'doctor': doctor,
        'reviews': reviews,
        'time_slots': time_slots,
        'user_review': user_review,
        'total_reviews': reviews.count(),
        'average_rating': doctor.average_rating,
    })


@login_required
def create_review(request, doctor_id):
    """Create or update a review"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    existing_review = DoctorReview.objects.filter(doctor=doctor, user=request.user).first()
    
    if request.method == 'POST':
        rating = request.POST.get('rating', 5)
        comment = request.POST.get('comment', '')
        
        if existing_review:
            existing_review.rating = int(rating)
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, "Review updated successfully.")
        else:
            DoctorReview.objects.create(
                doctor=doctor,
                user=request.user,
                rating=int(rating),
                comment=comment
            )
            doctor.total_reviews += 1
            doctor.average_rating = doctor.get_avg_rating()
            doctor.save()
            messages.success(request, "Your review has been saved.")
        
        return redirect('appointments:doctor_detail', doctor_id=doctor_id)
    
    return render(request, 'appointments/create_review.html', {
        'doctor': doctor,
        'existing_review': existing_review
    })


@login_required
def edit_review(request, doctor_id):
    """Edit an existing review"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    review = get_object_or_404(DoctorReview, doctor=doctor, user=request.user)
    
    if request.method == 'POST':
        review.rating = int(request.POST.get('rating', review.rating))
        review.comment = request.POST.get('comment', review.comment)
        review.save()
        
        doctor.average_rating = doctor.get_avg_rating()
        doctor.save()
        
        messages.success(request, "Review updated successfully.")
        return redirect('appointments:doctor_detail', doctor_id=doctor_id)
    
    return render(request, 'appointments/create_review.html', {
        'doctor': doctor,
        'existing_review': review,
        'is_edit': True
    })


@login_required
def delete_review(request, review_id):
    """Delete a review"""
    review = get_object_or_404(DoctorReview, id=review_id, user=request.user)
    doctor = review.doctor
    doctor_id = doctor.id
    
    doctor.total_reviews -= 1
    review.delete()
    doctor.average_rating = doctor.get_avg_rating()
    doctor.save()
    
    messages.success(request, "Review deleted successfully.")
    return redirect('appointments:doctor_detail', doctor_id=doctor_id)


def top_doctors(request):
    """Display top rated doctors"""
    doctors = Doctor.objects.filter(
        average_rating__gte=4.0
    ).order_by('-average_rating', '-total_reviews')[:10]
    
    return render(request, 'appointments/top_doctors.html', {
        'doctors': doctors,
        'total_doctors': doctors.count()
    })

