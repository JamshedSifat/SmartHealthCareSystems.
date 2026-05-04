from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, time, timedelta, datetime
from .models import Medicine, ReminderTime, DoseTaken
from .google_calendar_service import generate_google_calendar_url
import logging

logger = logging.getLogger(__name__)


@login_required
def add_reminder(request):
    """Add new medicine reminder"""
    if request.method == 'POST':
        name = request.POST.get('name')
        amount = request.POST.get('dosage_amount')
        unit = request.POST.get('dosage_unit')
        frequency = request.POST.get('frequency')
        food_timing = request.POST.get('food_timing', 'any')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        instructions = request.POST.get('instructions', '')
        doctor_name = request.POST.get('doctor_name', '')
        prescription_date = request.POST.get('prescription_date', '')
        times = request.POST.getlist('times[]')

        if not all([name, amount, unit, frequency, start, end]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('reminders:add_reminder')

        try:
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
            if start_date > end_date:
                messages.error(request, "Start date must be before end date.")
                return redirect('reminders:add_reminder')
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('reminders:add_reminder')

        medicine = Medicine.objects.create(
            user=request.user,
            name=name,
            dosage_amount=amount,
            dosage_unit=unit,
            frequency=frequency,
            food_timing=food_timing,
            start_date=start_date,
            end_date=end_date,
            instructions=instructions,
            doctor_name=doctor_name,
            prescription_date=prescription_date if prescription_date else None,
            is_active=True
        )

        if times and any(times):
            for time_str in times:
                if time_str:
                    try:
                        reminder_time = datetime.strptime(time_str, '%H:%M').time()
                        ReminderTime.objects.create(medicine=medicine, time=reminder_time)
                    except ValueError:
                        continue
        else:
            if frequency == 'once':
                ReminderTime.objects.create(medicine=medicine, time=time(8, 0))
            elif frequency == 'twice':
                ReminderTime.objects.create(medicine=medicine, time=time(8, 0))
                ReminderTime.objects.create(medicine=medicine, time=time(20, 0))
            elif frequency == 'thrice':
                ReminderTime.objects.create(medicine=medicine, time=time(8, 0))
                ReminderTime.objects.create(medicine=medicine, time=time(14, 0))
                ReminderTime.objects.create(medicine=medicine, time=time(20, 0))
            elif frequency == 'four':
                ReminderTime.objects.create(medicine=medicine, time=time(8, 0))
                ReminderTime.objects.create(medicine=medicine, time=time(12, 0))
                ReminderTime.objects.create(medicine=medicine, time=time(16, 0))
                ReminderTime.objects.create(medicine=medicine, time=time(20, 0))

        messages.success(request, f"✅ {name} reminder added successfully!")
        return redirect('reminders:dashboard')

    today = date.today()
    next_month = today + timedelta(days=30)

    context = {
        'today': today.isoformat(),
        'next_month': next_month.isoformat(),
    }
    return render(request, 'reminders/add_reminder.html', context)


@login_required
def edit_reminder(request, medicine_id):
    """Edit existing medicine reminder"""
    medicine = get_object_or_404(Medicine, id=medicine_id, user=request.user)

    if request.method == 'POST':
        medicine.name = request.POST.get('name')
        medicine.dosage_amount = request.POST.get('dosage_amount')
        medicine.dosage_unit = request.POST.get('dosage_unit')
        medicine.frequency = request.POST.get('frequency')
        medicine.food_timing = request.POST.get('food_timing', 'any')
        medicine.start_date = request.POST.get('start_date')
        medicine.end_date = request.POST.get('end_date')
        medicine.instructions = request.POST.get('instructions', '')
        medicine.doctor_name = request.POST.get('doctor_name', '')
        prescription_date = request.POST.get('prescription_date', '')
        medicine.prescription_date = prescription_date if prescription_date else None
        medicine.save()

        messages.success(request, f"✅ {medicine.name} reminder updated successfully!")
        return redirect('reminders:dashboard')

    context = {
        'medicine': medicine,
        'start_date': medicine.start_date.isoformat(),
        'end_date': medicine.end_date.isoformat(),
        'food_timing_choices': Medicine.FOOD_TIMING_CHOICES,
    }
    return render(request, 'reminders/edit_reminder.html', context)


@login_required
def delete_reminder(request, medicine_id):
    """Delete medicine reminder"""
    medicine = get_object_or_404(Medicine, id=medicine_id, user=request.user)

    if request.method == 'POST':
        name = medicine.name
        DoseTaken.objects.filter(medicine=medicine).delete()
        medicine.delete()
        messages.success(request, f"✅ {name} reminder deleted!")
        return redirect('reminders:dashboard')

    return render(request, 'reminders/delete_confirm.html', {'medicine': medicine})


@login_required
def mark_taken(request, medicine_id, reminder_time_id):
    """Mark a dose as taken"""
    medicine = get_object_or_404(Medicine, id=medicine_id, user=request.user)
    reminder_time = get_object_or_404(ReminderTime, id=reminder_time_id, medicine=medicine)
    
    if request.method == 'POST':
        today = date.today()
        now = timezone.now()
        
        dose, created = DoseTaken.objects.get_or_create(
            medicine=medicine,
            reminder_time=reminder_time,
            date_taken=today,
            defaults={'time_taken': now.time()}
        )
        
        if created:
            messages.success(request, f"✅ {medicine.name} marked as taken!")
        else:
            messages.info(request, f"ℹ️ {medicine.name} already marked as taken today.")
    
    return redirect('reminders:dashboard')


@login_required
def add_to_calendar(request, medicine_id, reminder_time_id):
    """ Direct redirect to Google Calendar with recurring event"""
    try:
        medicine = get_object_or_404(Medicine, id=medicine_id, user=request.user)
        reminder_time = get_object_or_404(ReminderTime, id=reminder_time_id, medicine=medicine)
        
        calendar_url = generate_google_calendar_url(medicine, reminder_time)
        logger.info(f"User {request.user.username} redirected to Google Calendar for {medicine.name}")
        
        return redirect(calendar_url)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        messages.error(request, f"❌ Error: {str(e)}")
        return redirect('reminders:dashboard')
