from django import forms
from .models import (
    DietaryPreference,
    Food,
    UserHealthProfile,
    DietPlan,
    Meal,
    DailyLog,
    MealFood,
    DailyMealLog,
)


# ===== EXISTING FORMS (Keep these) =====

class DietaryPreferenceForm(forms.ModelForm):
    """Form for dietary preferences"""
    
    class Meta:
        model = DietaryPreference
        fields = ['diet_type', 'is_strict', 'notes']
        widgets = {
            'diet_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'is_strict': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter any additional dietary notes...',
            }),
        }


class CompatibilityCheckForm(forms.Form):
    """Form for checking medicine compatibility"""
    
    medicine_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter medicine name...',
        }),
    )
    
    check_allergens = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label="Check for allergens",
    )


# ===== NEW DIET PLAN FORMS =====

class UserHealthProfileForm(forms.ModelForm):
    """Form for user health profile"""
    
    class Meta:
        model = UserHealthProfile
        fields = [
            'age', 'height', 'weight', 'gender',
            'activity_level', 'health_goal',
            'medical_conditions', 'allergies'
        ]
        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age in years',
                'min': '1',
                'max': '120',
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Height in cm',
                'step': '0.1',
                'min': '50',
                'max': '250',
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight in kg',
                'step': '0.1',
                'min': '20',
                'max': '500',
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
            }),
            'activity_level': forms.Select(attrs={
                'class': 'form-control',
            }),
            'health_goal': forms.Select(attrs={
                'class': 'form-control',
            }),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g., Diabetes, Hypertension',
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g., Peanuts, Shellfish',
            }),
        }


class FoodForm(forms.ModelForm):
    """Form for adding/editing food items"""
    
    class Meta:
        model = Food
        fields = [
            'name', 'food_type', 'calories', 'protein',
            'carbs', 'fat', 'fiber', 'serving_size', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Chicken Breast',
            }),
            'food_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calories per 100g',
                'min': '0',
            }),
            'protein': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Protein in grams',
                'step': '0.1',
                'min': '0',
            }),
            'carbs': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Carbs in grams',
                'step': '0.1',
                'min': '0',
            }),
            'fat': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fat in grams',
                'step': '0.1',
                'min': '0',
            }),
            'fiber': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fiber in grams',
                'step': '0.1',
                'min': '0',
            }),
            'serving_size': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '100g',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
        }


class DietPlanForm(forms.ModelForm):
    """Form for creating/editing diet plans"""
    
    class Meta:
        model = DietPlan
        fields = [
            'name', 'diet_type', 'target_calories',
            'target_protein', 'target_carbs', 'target_fat',
            'description', 'recommendations'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., High Protein Diet',
            }),
            'diet_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'target_calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Daily calorie target',
                'min': '500',
                'max': '5000',
            }),
            'target_protein': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Protein %',
                'min': '0',
                'max': '100',
            }),
            'target_carbs': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Carbs %',
                'min': '0',
                'max': '100',
            }),
            'target_fat': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fat %',
                'min': '0',
                'max': '100',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
            'recommendations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
        }


class MealForm(forms.ModelForm):
    """Form for creating/editing meals"""
    
    class Meta:
        model = Meal
        fields = [
            'name', 'meal_type', 'preparation_time',
            'difficulty_level', 'instructions', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Grilled Chicken with Rice',
            }),
            'meal_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'preparation_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minutes',
                'min': '1',
                'max': '480',
            }),
            'difficulty_level': forms.Select(attrs={
                'class': 'form-control',
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Step-by-step cooking instructions',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tips and additional notes',
            }),
        }


class DailyLogForm(forms.ModelForm):
    """Form for creating/editing daily nutrition logs"""
    
    class Meta:
        model = DailyLog
        fields = ['date', 'weight', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight in kg',
                'step': '0.1',
                'min': '20',
                'max': '500',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Daily observations or notes',
            }),
        }


class MealFoodForm(forms.ModelForm):
    """Form for adding foods to meals"""
    
    class Meta:
        model = MealFood
        fields = ['food', 'quantity']
        widgets = {
            'food': forms.Select(attrs={
                'class': 'form-control',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quantity in grams',
                'step': '1',
                'min': '1',
            }),
        }


class DailyMealLogForm(forms.ModelForm):
    """Form for logging meals in daily log"""
    
    class Meta:
        model = DailyMealLog
        fields = ['meal', 'serving_multiplier', 'time_consumed']
        widgets = {
            'meal': forms.Select(attrs={
                'class': 'form-control',
            }),
            'serving_multiplier': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'How many times (1 = full meal)',
                'step': '0.1',
                'min': '0.1',
                'max': '10',
            }),
            'time_consumed': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
        }
