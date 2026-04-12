from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from .models import *

def appointment(request):
    doctors = Doctor.objects.all()
    return render(request, "appointments/appointment.html", {'doctors': doctors})

def doctor_search(request):
    query_d = request.GET.get('q')

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

    return render(request, 'appointments/appointment.html', {'doctors': doctors})

@login_required
def create_appointment(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)

    if request.method == 'POST':
        appointment_date = request.POST['appointment_date']
        description = request.POST['description']
        appointment_time_id = request.POST['appointment_time']
        time_slot = DoctorTimeSlot.objects.get(id=appointment_time_id, doctor=doctor)
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

        serial_number = Appointment.objects.filter(doctor=doctor).count() + 1

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

        messages.success(request, "Successful appointment made")
        return redirect(reverse('appointments:appointment'))

    return render(request, 'appointments/create_appointment.html', {'doctor': doctor})

def cancel_appointment(request, appointment_id, doctor_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if appointment.user == request.user:
        doctor.available_spots += 1
        doctor.save()
        appointment.delete()
        messages.success(request, "Appointment canceled successfully.")
    else:
        messages.error(request, "You are not authorized to cancel this appointment.")

    return redirect('accounts:user_profile')
