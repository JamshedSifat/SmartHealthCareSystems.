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
