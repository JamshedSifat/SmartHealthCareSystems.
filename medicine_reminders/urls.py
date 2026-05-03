from django.urls import path
from . import views

app_name = 'reminders'

urlpatterns = [
    path('dashboard/', views.reminders_home, name='dashboard'),
    path('add/', views.add_reminder, name='add_reminder'),
    path('edit/<int:medicine_id>/', views.edit_reminder, name='edit_reminder'),
    path('delete/<int:medicine_id>/', views.delete_reminder, name='delete_reminder'),
    path('mark-taken/<int:medicine_id>/<int:reminder_time_id>/', views.mark_taken, name='mark_taken'),
    path('history/', views.reminder_history, name='history'),
    path('list/', views.reminders_list, name='reminders_list'),
    path('add-to-calendar/<int:medicine_id>/<int:reminder_time_id>/', views.add_to_calendar, name='add_to_calendar'),
]
