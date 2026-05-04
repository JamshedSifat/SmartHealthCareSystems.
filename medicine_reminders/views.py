from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, time, timedelta, datetime
from .google_calendar_service import generate_google_calendar_url
import logging

logger = logging.getLogger(__name__)

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
