from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Medicine, ReminderTime, DoseTaken


class ReminderTimeInline(admin.TabularInline):
    model = ReminderTime
    extra = 1
    fields = ['time']
    verbose_name = "Reminder Time"
    verbose_name_plural = "Reminder Times"


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'user_link',
        'dosage_display',
        'frequency_display',
        'date_range',
        'doctor_display',
        'is_active',
        'reminder_count',
        'created_at'
    ]

    list_filter = [
        'is_active',
        'frequency',
        'dosage_unit',
        'food_timing',
        'created_at',
        'start_date',
        'end_date'
    ]

    search_fields = [
        'name',
        'doctor_name',
        'user__username',
        'user__first_name',
        'user__last_name',
        'instructions'
    ]

    list_editable = ['is_active']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fields = [
        'user',
        'name',
        ('dosage_amount', 'dosage_unit'),
        'frequency',
        'food_timing',
        ('start_date', 'end_date'),
        ('doctor_name', 'prescription_date'),
        'instructions',
        'is_active',
        ('created_at', 'updated_at')
    ]

    inlines = [ReminderTimeInline]
    list_per_page = 25

    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'

    def dosage_display(self, obj):
        return f"{obj.dosage_amount} {obj.get_dosage_unit_display()}"
    dosage_display.short_description = 'Dosage'
    dosage_display.admin_order_field = 'dosage_amount'

    def frequency_display(self, obj):
        colors = {
            'once': '#28a745',
            'twice': '#ffc107',
            'thrice': '#fd7e14',
            'four': '#dc3545'
        }
        color = colors.get(obj.frequency, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_frequency_display()
        )
    frequency_display.short_description = 'Frequency'
    frequency_display.admin_order_field = 'frequency'

    def date_range(self, obj):
        return f"{obj.start_date} to {obj.end_date}"
    date_range.short_description = 'Date Range'
    date_range.admin_order_field = 'start_date'

    def doctor_display(self, obj):
        if obj.doctor_name:
            return format_html('<span style="color: #0066cc;">👨‍⚕️ {}</span>', obj.doctor_name)
        return '-'
    doctor_display.short_description = 'Doctor'
    doctor_display.admin_order_field = 'doctor_name'

    def reminder_count(self, obj):
        count = obj.reminder_times.count()
        return f"{count} time{'s' if count != 1 else ''}"
    reminder_count.short_description = 'Reminders'

    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} medicine(s) marked as active.')
    make_active.short_description = "Mark selected medicines as active"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} medicine(s) marked as inactive.')
    make_inactive.short_description = "Mark selected medicines as inactive"


@admin.register(ReminderTime)
class ReminderTimeAdmin(admin.ModelAdmin):
    list_display = ['medicine_name', 'user_name', 'time_display', 'medicine_active']
    list_filter = ['time', 'medicine__is_active', 'medicine__user']
    search_fields = ['medicine__name', 'medicine__user__username']
    ordering = ['medicine__name', 'time']

    def medicine_name(self, obj):
        url = reverse('admin:medicine_reminders_medicine_change', args=[obj.medicine.id])
        return format_html('<a href="{}">{}</a>', url, obj.medicine.name)
    medicine_name.short_description = 'Medicine'
    medicine_name.admin_order_field = 'medicine__name'

    def user_name(self, obj):
        return obj.medicine.user.username
    user_name.short_description = 'User'
    user_name.admin_order_field = 'medicine__user__username'

    def time_display(self, obj):
        return obj.time.strftime('%I:%M %p')
    time_display.short_description = 'Time'
    time_display.admin_order_field = 'time'

    def medicine_active(self, obj):
        if obj.medicine.is_active:
            return format_html('<span style="color: green;">✅</span>')
        else:
            return format_html('<span style="color: red;">❌</span>')
    medicine_active.short_description = 'Active'
    medicine_active.admin_order_field = 'medicine__is_active'


@admin.register(DoseTaken)
class DoseTakenAdmin(admin.ModelAdmin):
    list_display = [
        'medicine_name',
        'user_name',
        'date_taken',
        'time_taken_display',
        'scheduled_time',
        'created_at'
    ]
    list_filter = [
        'date_taken',
        'created_at',
        'medicine__user',
        'medicine__name'
    ]
    search_fields = [
        'medicine__name',
        'medicine__user__username'
    ]
    readonly_fields = ['created_at']
    ordering = ['-date_taken', '-time_taken']
    date_hierarchy = 'date_taken'

    def medicine_name(self, obj):
        url = reverse('admin:medicine_reminders_medicine_change', args=[obj.medicine.id])
        return format_html('<a href="{}">{}</a>', url, obj.medicine.name)
    medicine_name.short_description = 'Medicine'
    medicine_name.admin_order_field = 'medicine__name'

    def user_name(self, obj):
        return obj.medicine.user.username
    user_name.short_description = 'User'
    user_name.admin_order_field = 'medicine__user__username'

    def time_taken_display(self, obj):
        return obj.time_taken.strftime('%I:%M %p')
    time_taken_display.short_description = 'Time Taken'
    time_taken_display.admin_order_field = 'time_taken'

    def scheduled_time(self, obj):
        return obj.reminder_time.time.strftime('%I:%M %p')
    scheduled_time.short_description = 'Scheduled'
    scheduled_time.admin_order_field = 'reminder_time__time'


admin.site.site_header = "E-Seba Healthcare Admin"
admin.site.site_title = "E-Seba Admin Portal"
admin.site.index_title = "Welcome to E-Seba Healthcare Administration"
