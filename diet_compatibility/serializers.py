from rest_framework import serializers
from .models import (
    Food,
    UserHealthProfile,
    DietPlan,
    Meal,
    MealFood,
    DailyLog,
    DailyMealLog,
)


class FoodSerializer(serializers.ModelSerializer):
    """Serializer for Food model"""
    
    food_type_display = serializers.CharField(
        source='get_food_type_display',
        read_only=True
    )
    
    class Meta:
        model = Food
        fields = [
            'id', 'name', 'food_type', 'food_type_display',
            'calories', 'protein', 'carbs', 'fat', 'fiber',
            'serving_size', 'description', 'is_approved',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserHealthProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserHealthProfile model"""
    
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    activity_level_display = serializers.CharField(source='get_activity_level_display', read_only=True)
    health_goal_display = serializers.CharField(source='get_health_goal_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserHealthProfile
        fields = [
            'id', 'username', 'age', 'height', 'weight', 'gender',
            'gender_display', 'activity_level', 'activity_level_display',
            'health_goal', 'health_goal_display',
            'medical_conditions', 'allergies',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DietPlanSerializer(serializers.ModelSerializer):
    """Serializer for DietPlan model"""
    
    diet_type_display = serializers.CharField(source='get_diet_type_display', read_only=True)
    macro_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = DietPlan
        fields = [
            'id', 'name', 'diet_type', 'diet_type_display',
            'target_calories', 'target_protein', 'target_carbs',
            'target_fat', 'description', 'recommendations',
            'is_active', 'macro_breakdown',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'macro_breakdown']
    
    def get_macro_breakdown(self, obj):
        """Get macro breakdown for the diet plan"""
        return obj.get_macro_breakdown()


class MealFoodSerializer(serializers.ModelSerializer):
    """Serializer for MealFood (through model)"""
    
    food_name = serializers.CharField(source='food.name', read_only=True)
    food_calories = serializers.IntegerField(source='food.calories', read_only=True)
    total_calories = serializers.SerializerMethodField()
    macros = serializers.SerializerMethodField()
    
    class Meta:
        model = MealFood
        fields = [
            'id', 'meal', 'food', 'food_name', 'quantity',
            'food_calories', 'total_calories', 'macros'
        ]
    
    def get_total_calories(self, obj):
        """Get total calories for this food in meal"""
        return obj.get_calories()
    
    def get_macros(self, obj):
        """Get macros for this food in meal"""
        return obj.get_macros()


class MealSerializer(serializers.ModelSerializer):
    """Serializer for Meal model"""
    
    meal_type_display = serializers.CharField(source='get_meal_type_display', read_only=True)
    difficulty_level_display = serializers.CharField(source='get_difficulty_level_display', read_only=True)
    foods_detail = MealFoodSerializer(source='mealfood_set', many=True, read_only=True)
    total_calories = serializers.SerializerMethodField()
    total_macros = serializers.SerializerMethodField()
    
    class Meta:
        model = Meal
        fields = [
            'id', 'name', 'meal_type', 'meal_type_display',
            'preparation_time', 'difficulty_level', 'difficulty_level_display',
            'instructions', 'notes', 'is_published',
            'foods_detail', 'total_calories', 'total_macros',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_calories(self, obj):
        """Get total calories in meal"""
        return obj.get_total_calories()
    
    def get_total_macros(self, obj):
        """Get total macros in meal"""
        return obj.get_total_macros()


class DailyMealLogSerializer(serializers.ModelSerializer):
    """Serializer for DailyMealLog"""
    
    meal_name = serializers.CharField(source='meal.name', read_only=True)
    meal_type = serializers.CharField(source='meal.meal_type', read_only=True)
    calories = serializers.SerializerMethodField()
    macros = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyMealLog
        fields = [
            'id', 'daily_log', 'meal', 'meal_name', 'meal_type',
            'serving_multiplier', 'time_consumed', 'calories', 'macros'
        ]
    
    def get_calories(self, obj):
        """Get calories for this meal log"""
        return obj.get_calories()
    
    def get_macros(self, obj):
        """Get macros for this meal log"""
        return obj.get_macros()


class DailyLogSerializer(serializers.ModelSerializer):
    """Serializer for DailyLog model"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    meals_detail = DailyMealLogSerializer(source='dailymeallog_set', many=True, read_only=True)
    total_calories = serializers.SerializerMethodField()
    total_macros = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyLog
        fields = [
            'id', 'user', 'username', 'date', 'weight', 'notes',
            'is_complete', 'meals_detail',
            'total_calories', 'total_macros',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_calories(self, obj):
        """Get total calories for the day"""
        return obj.get_total_calories()
    
    def get_total_macros(self, obj):
        """Get total macros for the day"""
        return obj.get_total_macros()
