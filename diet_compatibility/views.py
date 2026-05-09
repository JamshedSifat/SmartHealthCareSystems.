
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import timedelta, datetime

from .models import (
    Disease, Food, DiseaseFood, Medicine, MedicineFoodCompatibility,
    HealthProfile, MealPlan, MealFood, DailyLog, Allergy
)
# ============ DASHBOARD ============
@login_required
def health_dashboard(request):
    """Main health dashboard"""
    
    # ✅ FIX: Check if profile exists, if not create one
    profile, created = HealthProfile.objects.get_or_create(user=request.user)
    
    if created:
        # Set default values
        profile.age = 25
        profile.height = 170.0
        profile.weight = 70.0
        profile.gender = 'male'
        profile.activity_level = 'moderate'
        profile.save()
        messages.info(request, "Please complete your health profile!")
        return redirect('diet_compatibility:create_health_profile')
    
    today = timezone.now().date()
    daily_log, _ = DailyLog.objects.get_or_create(user=request.user, date=today)
    
    # Today's meals
    today_meals = MealPlan.objects.filter(user=request.user, date=today)
    today_calories = sum(meal.get_total_calories() for meal in today_meals)
    
    # Health stats
    bmi = profile.calculate_bmi()
    bmi_category = profile.get_bmi_category()
    daily_calorie_need = profile.calculate_daily_calorie_need()
    water_goal = 2000  # ml
    
    # Recommendations
    diseases = profile.diseases.all()
    medicines = profile.medicines.all()
    
    # User allergies
    try:
        allergies = request.user.allergy_profile.foods.all()
    except:
        allergies = []
    
    # Format today's date
    today_date = today.strftime("%A, %B %d, %Y")
    
    context = {
        'profile': profile,
        'bmi': bmi,
        'bmi_category': bmi_category,
        'daily_calorie_need': daily_calorie_need,
        'today_calories': today_calories,
        'water_intake': daily_log.water_intake_ml,
        'water_goal': water_goal,
        'today_meals': today_meals,
        'diseases': diseases,
        'medicines': medicines,
        'allergies': allergies,
        'today_date': today_date,
    }
    
    return render(request, 'diet_compatibility/dashboard.html', context)

# ============ DISEASE DIET ============
@login_required
def disease_diet_suggestion(request):
    """Disease-based diet suggestions"""
    diseases = Disease.objects.all()
    
    selected_disease = request.GET.get('disease')
    disease_obj = None
    recommended_foods = []
    avoid_foods = []
    limited_foods = []
    
    if selected_disease:
        disease_obj = get_object_or_404(Disease, id=selected_disease)
        
        disease_foods = DiseaseFood.objects.filter(disease=disease_obj)
        
        recommended_foods = disease_foods.filter(status='recommended').select_related('food')
        avoid_foods = disease_foods.filter(status='avoid').select_related('food')
        limited_foods = disease_foods.filter(status='limited').select_related('food')
    
    context = {
        'diseases': diseases,
        'disease_obj': disease_obj,
        'recommended_foods': recommended_foods,
        'avoid_foods': avoid_foods,
        'limited_foods': limited_foods,
    }
    
    return render(request, 'diet_compatibility/disease_diet.html', context)


@login_required
def disease_detail(request, disease_id):
    """Disease detail page"""
    disease = get_object_or_404(Disease, id=disease_id)
    disease_foods = DiseaseFood.objects.filter(disease=disease)
    
    context = {
        'disease': disease,
        'disease_foods': disease_foods,
    }
    
    return render(request, 'diet_compatibility/disease_detail.html', context)


# ============ MEAL PLANNING ============
@login_required
def meal_plan(request):
    """View meal plans"""
    today = timezone.now().date()
    meals = MealPlan.objects.filter(user=request.user, date=today)
    
    total_calories = sum(meal.get_total_calories() for meal in meals)
    daily_need = 2000
    
    try:
        daily_need = request.user.health_profile.calculate_daily_calorie_need()
    except:
        pass
    
    context = {
        'meals': meals,
        'total_calories': total_calories,
        'daily_need': daily_need,
    }
    
    return render(request, 'diet_compatibility/meal_plan.html', context)


@login_required
def create_meal(request):
    """Create meal plan"""
    if request.method == 'POST':
        meal_type = request.POST.get('meal_type')
        date_str = request.POST.get('date')
        
        if not date_str:
            date_str = timezone.now().date()
        
        meal, created = MealPlan.objects.get_or_create(
            user=request.user,
            meal_type=meal_type,
            date=date_str
        )
        
        # Remove existing foods
        meal.mealfood_set.all().delete()
        
        # Add foods
        food_ids = request.POST.getlist('food_ids')
        quantities = request.POST.getlist('quantities')
        
        for food_id, quantity in zip(food_ids, quantities):
            if food_id and quantity:
                try:
                    food = Food.objects.get(id=food_id)
                    MealFood.objects.create(
                        meal_plan=meal,
                        food=food,
                        quantity_grams=int(quantity)
                    )
                except:
                    pass
        
        messages.success(request, "Meal created successfully!")
        return redirect('diet_compatibility:meal_plan')
    
    foods = Food.objects.all()
    
    context = {
        'foods': foods,
    }
    
    return render(request, 'diet_compatibility/create_meal.html', context)


@login_required
def delete_meal(request, meal_id):
    """Delete meal"""
    meal = get_object_or_404(MealPlan, id=meal_id, user=request.user)
    meal.delete()
    messages.success(request, "Meal deleted!")
    return redirect('diet_compatibility:meal_plan')



# ============ RECOMMENDATIONS ============
@login_required
def get_recommendations(request):
    """Get personalized health recommendations"""
    try:
        profile = request.user.health_profile
    except HealthProfile.DoesNotExist:
        messages.error(request, "Please create health profile!")
        return redirect('diet_compatibility:create_health_profile')
    
    recommendations = []
    
    # BMI recommendations
    bmi = profile.calculate_bmi()
    if bmi < 18.5:
        recommendations.append({
            'type': 'BMI',
            'title': 'Underweight',
            'description': 'Increase calorie intake with nutrient-rich foods',
            'priority': 'high',
            'icon': '📉'
        })
    elif bmi > 25:
        recommendations.append({
            'type': 'BMI',
            'title': 'Overweight',
            'description': 'Focus on calorie-controlled diet and exercise',
            'priority': 'high',
            'icon': '📈'
        })
    else:
        recommendations.append({
            'type': 'BMI',
            'title': 'Healthy Weight',
            'description': 'Maintain your current healthy lifestyle',
            'priority': 'low',
            'icon': '✅'
        })
    
    # Disease-specific recommendations
    for disease in profile.diseases.all():
        recommendations.append({
            'type': 'Disease',
            'title': f'Diet for {disease.name}',
            'description': disease.description,
            'priority': 'high' if disease.severity_level == 'severe' else 'medium',
            'icon': '🩺'
        })
    
    # Medicine-specific recommendations
    for medicine in profile.medicines.all():
        interactions = MedicineFoodCompatibility.objects.filter(
            medicine=medicine,
            interaction_level='avoid'
        ).count()
        
        if interactions > 0:
            recommendations.append({
                'type': 'Medicine',
                'title': f'Be careful with {medicine.name}',
                'description': f'{interactions} food interactions found',
                'priority': 'medium',
                'icon': '💊'
            })
    
    context = {
        'recommendations': recommendations,
    }
    
    return render(request, 'diet_compatibility/recommendations.html', context)

