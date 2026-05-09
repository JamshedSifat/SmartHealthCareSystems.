from django.contrib import admin
from .models import (
    Disease, Food, DiseaseFood, Medicine, MedicineFoodCompatibility,
    HealthProfile, MealPlan, MealFood, DailyLog, Allergy
)

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'severity_level']
    search_fields = ['name']

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'calories_per_100g', 'protein', 'carbs', 'fat']
    list_filter = ['category']
    search_fields = ['name']

@admin.register(DiseaseFood)
class DiseaseFoodAdmin(admin.ModelAdmin):
    list_display = ['disease', 'food', 'status']
    list_filter = ['status', 'disease']

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name', 'purpose']
    search_fields = ['name', 'generic_name']

@admin.register(MedicineFoodCompatibility)
class MedicineFoodCompatibilityAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'food', 'interaction_level']
    list_filter = ['interaction_level']

@admin.register(HealthProfile)
class HealthProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'height', 'weight', 'activity_level']
    filter_horizontal = ['diseases', 'medicines']  # ✅ REMOVED 'allergies'

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'meal_type', 'date']
    list_filter = ['meal_type', 'date']

@admin.register(MealFood)
class MealFoodAdmin(admin.ModelAdmin):
    list_display = ['meal_plan', 'food', 'quantity_grams']

@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'water_intake_ml']
    list_filter = ['date']

@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ['user']
    filter_horizontal = ['foods']  
