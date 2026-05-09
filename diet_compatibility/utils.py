"""
Utility functions for diet compatibility and nutrition calculations.
Beginner-friendly functions for BMI, calorie tracking, and diet suggestions.
"""
import math
from datetime import date, timedelta


# ===== BMI CALCULATION =====

def calculate_bmi(weight, height):
    """
    Calculate Body Mass Index (BMI).
    
    Args:
        weight: Weight in kilograms
        height: Height in centimeters
    
    Returns:
        dict: BMI value and health category
    
    Example:
        result = calculate_bmi(70, 175)
        # Returns: {'bmi': 22.86, 'category': 'Normal weight'}
    """
    # Convert height to meters
    height_meters = height / 100
    
    # Calculate BMI: weight (kg) / height (m)^2
    bmi = weight / (height_meters ** 2)
    
    # Determine category
    if bmi < 18.5:
        category = 'Underweight'
        color = 'warning'  # Yellow
    elif 18.5 <= bmi < 25:
        category = 'Normal weight'
        color = 'success'  # Green
    elif 25 <= bmi < 30:
        category = 'Overweight'
        color = 'warning'  # Yellow
    else:
        category = 'Obese'
        color = 'danger'  # Red
    
    return {
        'bmi': round(bmi, 2),
        'category': category,
        'color': color,
        'health_status': get_bmi_health_advice(bmi),
    }


def get_bmi_health_advice(bmi):
    """
    Get health advice based on BMI value.
    
    Args:
        bmi: BMI value
    
    Returns:
        str: Health advice message
    """
    if bmi < 18.5:
        return "You may be underweight. Consider consulting a nutritionist."
    elif 18.5 <= bmi < 25:
        return "You have a healthy weight. Keep up the good work!"
    elif 25 <= bmi < 30:
        return "You may be overweight. Regular exercise and diet can help."
    else:
        return "Obesity detected. Please consult a healthcare provider."




# ===== CALORIE CALCULATION =====

def calculate_daily_calorie_requirement(age, weight, height, gender, activity_level):
    """
    Calculate daily calorie requirement using Harris-Benedict equation.
    
    Args:
        age: Age in years
        weight: Weight in kilograms
        height: Height in centimeters
        gender: 'M' for Male, 'F' for Female
        activity_level: Activity level ('sedentary', 'light', 'moderate', 'active', 'very_active')
    
    Returns:
        dict: BMR, TDEE, and daily calorie recommendation
    
    Example:
        result = calculate_daily_calorie_requirement(25, 70, 175, 'M', 'moderate')
        # Returns: {'bmr': 1700, 'tdee': 2550, 'recommendation': 2300}
    """
    # Step 1: Calculate Basal Metabolic Rate (BMR)
    if gender == 'M':
        # Harris-Benedict equation for males
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        # Harris-Benedict equation for females
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    
    # Step 2: Apply activity level multiplier
    activity_multipliers = {
        'sedentary': 1.2,        # Little or no exercise
        'light': 1.375,          # Exercise 1-3 days/week
        'moderate': 1.55,        # Exercise 3-5 days/week
        'active': 1.725,         # Exercise 6-7 days/week
        'very_active': 1.9,      # Twice per day
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.55)
    tdee = bmr * multiplier  # Total Daily Energy Expenditure
    
    # Step 3: Adjust for weight loss goal (reduce by 500 cal)
    recommendation = tdee - 500 if tdee > 1200 else tdee
    
    return {
        'bmr': round(bmr, 0),
        'tdee': round(tdee, 0),
        'recommendation': round(recommendation, 0),
        'activity_level': activity_level,
    }


def calculate_macro_targets(daily_calories, protein_percentage=25, carbs_percentage=50, fat_percentage=25):
    """
    Calculate daily macronutrient targets based on percentages.
    
    Args:
        daily_calories: Daily calorie target
        protein_percentage: Protein as % of calories (default 25%)
        carbs_percentage: Carbs as % of calories (default 50%)
        fat_percentage: Fat as % of calories (default 25%)
    
    Returns:
        dict: Grams of protein, carbs, and fat
    
    Example:
        targets = calculate_macro_targets(2000)
        # Returns: {'protein': 125, 'carbs': 250, 'fat': 56}
    """
    # Verify percentages add up to 100
    total_percentage = protein_percentage + carbs_percentage + fat_percentage
    
    if total_percentage != 100:
        # Normalize percentages if they don't add up to 100
        protein_percentage = (protein_percentage / total_percentage) * 100
        carbs_percentage = (carbs_percentage / total_percentage) * 100
        fat_percentage = (fat_percentage / total_percentage) * 100
    
    # Calculate calories for each macro
    protein_calories = (daily_calories * protein_percentage) / 100
    carbs_calories = (daily_calories * carbs_percentage) / 100
    fat_calories = (daily_calories * fat_percentage) / 100
    
    # Convert to grams (Protein and Carbs: 4 cal/gram, Fat: 9 cal/gram)
    return {
        'protein_grams': round(protein_calories / 4, 1),
        'carbs_grams': round(carbs_calories / 4, 1),
        'fat_grams': round(fat_calories / 9, 1),
        'total_calories': daily_calories,
    }


def get_calorie_burn_estimate(activity_level, weight):
    """
    Estimate calories burned through daily activity.
    
    Args:
        activity_level: Activity level string
        weight: Weight in kilograms
    
    Returns:
        int: Estimated calories burned
    """
    # Approximate calories burned per kg per activity level
    burn_rates = {
        'sedentary': 0.5,
        'light': 1.0,
        'moderate': 1.5,
        'active': 2.0,
        'very_active': 2.5,
    }
    
    rate = burn_rates.get(activity_level, 1.5)
    return int(weight * rate * 24)  # Daily burn


# ===== DIET SUGGESTION =====

def suggest_diet_plan(bmi, health_goal, daily_calories):
    """
    Suggest appropriate diet based on health profile.
    
    Args:
        bmi: BMI value
        health_goal: Health goal ('weight_loss', 'weight_gain', 'muscle_gain', 'maintenance', 'fitness')
        daily_calories: Daily calorie requirement
    
    Returns:
        dict: Recommended diet plan with macros
    
    Example:
        suggestion = suggest_diet_plan(27, 'weight_loss', 1800)
        # Returns recommended diet with specific macros
    """
    suggestions = {}
    
    # Weight loss diet: Low carb, high protein
    if health_goal == 'weight_loss':
        suggestions = {
            'name': 'Weight Loss Plan',
            'description': 'High protein, moderate carbs, low fat diet for sustainable weight loss',
            'protein_percentage': 30,
            'carbs_percentage': 40,
            'fat_percentage': 30,
            'calorie_deficit': 500,
            'tips': [
                'Drink plenty of water',
                'Eat high protein foods to preserve muscle',
                'Avoid processed foods and sugary drinks',
                'Regular exercise is recommended',
            ]
        }
    
    # Weight gain diet: High calorie, balanced macros
    elif health_goal == 'weight_gain':
        suggestions = {
            'name': 'Weight Gain Plan',
            'description': 'High calorie, balanced diet for healthy weight gain',
            'protein_percentage': 25,
            'carbs_percentage': 50,
            'fat_percentage': 25,
            'calorie_surplus': 500,
            'tips': [
                'Eat frequent meals (5-6 times per day)',
                'Include calorie-dense foods like nuts and avocados',
                'Stay hydrated',
                'Combine with strength training',
            ]
        }
    
    # Muscle gain diet: High protein, moderate calories
    elif health_goal == 'muscle_gain':
        suggestions = {
            'name': 'Muscle Building Plan',
            'description': 'High protein diet with moderate calorie surplus for muscle growth',
            'protein_percentage': 35,
            'carbs_percentage': 45,
            'fat_percentage': 20,
            'calorie_surplus': 300,
            'tips': [
                'Consume protein with every meal',
                'Time carbs around workouts',
                'Strength training is essential',
                'Get adequate sleep (7-9 hours)',
            ]
        }
    
    # Maintenance diet: Balanced macros
    else:  # maintenance or fitness
        suggestions = {
            'name': 'Maintenance/Balanced Diet',
            'description': 'Balanced diet for healthy weight maintenance',
            'protein_percentage': 25,
            'carbs_percentage': 50,
            'fat_percentage': 25,
            'calorie_surplus': 0,
            'tips': [
                'Eat a variety of whole foods',
                'Include fruits and vegetables daily',
                'Regular physical activity',
                'Monitor your weight weekly',
            ]
        }
    
    # Calculate macros for the suggested plan
    macros = calculate_macro_targets(
        daily_calories,
        suggestions['protein_percentage'],
        suggestions['carbs_percentage'],
        suggestions['fat_percentage']
    )
    
    suggestions.update(macros)
    suggestions['recommended_calories'] = daily_calories
    
    return suggestions


def analyze_daily_nutrition(daily_log, diet_plan):
    """
    Analyze how close user got to their daily nutrition goals.
    
    Args:
        daily_log: DailyLog instance
        diet_plan: DietPlan instance
    
    Returns:
        dict: Analysis with progress percentages
    """
    actual_macros = daily_log.get_total_macros()
    actual_calories = daily_log.get_total_calories()
    target_macros = diet_plan.get_macro_breakdown()
    
    # Calculate percentages
    calorie_percentage = (actual_calories / diet_plan.target_calories) * 100 if diet_plan.target_calories > 0 else 0
    protein_percentage = (actual_macros['protein'] / target_macros['protein_grams']) * 100 if target_macros['protein_grams'] > 0 else 0
    carbs_percentage = (actual_macros['carbs'] / target_macros['carbs_grams']) * 100 if target_macros['carbs_grams'] > 0 else 0
    fat_percentage = (actual_macros['fat'] / target_macros['fat_grams']) * 100 if target_macros['fat_grams'] > 0 else 0
    
    return {
        'actual_calories': round(actual_calories, 0),
        'target_calories': diet_plan.target_calories,
        'calorie_percentage': round(calorie_percentage, 1),
        
        'actual_protein': round(actual_macros['protein'], 1),
        'target_protein': round(target_macros['protein_grams'], 1),
        'protein_percentage': round(protein_percentage, 1),
        
        'actual_carbs': round(actual_macros['carbs'], 1),
        'target_carbs': round(target_macros['carbs_grams'], 1),
        'carbs_percentage': round(carbs_percentage, 1),
        
        'actual_fat': round(actual_macros['fat'], 1),
        'target_fat': round(target_macros['fat_grams'], 1),
        'fat_percentage': round(fat_percentage, 1),
        
        'status': get_nutrition_status(calorie_percentage),
    }


def get_nutrition_status(calorie_percentage):
    """Get nutrition status based on calorie percentage."""
    if calorie_percentage < 80:
        return 'Under Target'
    elif 80 <= calorie_percentage <= 120:
        return 'On Target'
    else:
        return 'Over Target'


def get_nutrition_streak(user, days=7):
    """
    Calculate how many days in a row user logged their nutrition.
    
    Args:
        user: User instance
        days: How many days to check (default 7)
    
    Returns:
        dict: Streak information
    """
    from diet_compatibility.models import DailyLog
    
    streak = 0
    current_date = date.today()
    
    for i in range(days):
        check_date = current_date - timedelta(days=i)
        
        # Check if log exists for this date
        log_exists = DailyLog.objects.filter(
            user=user,
            date=check_date
        ).exists()
        
        if log_exists:
            streak += 1
        else:
            break  # Streak breaks if any day is missing
    
    return {
        'streak': streak,
        'message': f"Great! {streak} day streak!" if streak > 0 else "Start logging to build your streak!",
        'best_possible': days,
    }


def compare_nutrition_history(user, days=30):
    """
    Compare nutrition data over a period of time.
    
    Args:
        user: User instance
        days: Number of days to analyze
    
    Returns:
        dict: Statistics and trends
    """
    from diet_compatibility.models import DailyLog
    from django.db.models import Avg
    
    start_date = date.today() - timedelta(days=days)
    
    logs = DailyLog.objects.filter(
        user=user,
        date__gte=start_date
    )
    
    if not logs.exists():
        return {
            'average_calories': 0,
            'average_protein': 0,
            'average_carbs': 0,
            'average_fat': 0,
            'total_logs': 0,
            'trend': 'No data available',
        }
    
    # Get first and last log
    first_log = logs.first()
    last_log = logs.last()
    
    # Calculate average weight change
    weight_change = 0
    if first_log.weight and last_log.weight:
        weight_change = round(last_log.weight - first_log.weight, 2)
    
    return {
        'total_logs': logs.count(),
        'weight_change': weight_change,
        'weight_change_unit': 'kg',
        'days_analyzed': days,
        'message': f"You logged {logs.count()} days out of {days}" if logs.count() > 0 else "No logs found",
    }