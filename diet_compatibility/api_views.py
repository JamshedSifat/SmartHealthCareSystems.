"""
Django REST Framework API views for diet compatibility system.
Simple, beginner-friendly API endpoints for CRUD operations.
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q
from datetime import date, timedelta

from .models import (
    Food,
    UserHealthProfile,
    DietPlan,
    Meal,
    DailyLog,
)
from .serializers import (
    FoodSerializer,
    UserHealthProfileSerializer,
    DietPlanSerializer,
    MealSerializer,
    DailyLogSerializer,
)
from .utils import (
    calculate_bmi,
    calculate_daily_calorie_requirement,
    suggest_diet_plan,
    analyze_daily_nutrition,
)


# ===== PAGINATION =====

class StandardPagination(PageNumberPagination):
    """Standard pagination for API responses"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ===== FOOD VIEWSET =====

class FoodViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Food model.
    Allows CRUD operations on food items.
    """
    queryset = Food.objects.filter(is_approved=True)
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'food_type', 'description']
    ordering_fields = ['name', 'calories', 'protein', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter foods based on query parameters"""
        queryset = Food.objects.filter(is_approved=True)
        
        # Filter by food type
        food_type = self.request.query_params.get('food_type', None)
        if food_type:
            queryset = queryset.filter(food_type=food_type)
        
        # Filter by calorie range
        min_calories = self.request.query_params.get('min_calories', None)
        max_calories = self.request.query_params.get('max_calories', None)
        
        if min_calories:
            queryset = queryset.filter(calories__gte=int(min_calories))
        if max_calories:
            queryset = queryset.filter(calories__lte=int(max_calories))
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get foods grouped by type"""
        food_type = request.query_params.get('type', None)
        
        if not food_type:
            return Response(
                {'error': 'Please specify a food type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        foods = Food.objects.filter(
            food_type=food_type,
            is_approved=True
        )
        serializer = self.get_serializer(foods, many=True)
        
        return Response({
            'food_type': food_type,
            'count': len(foods),
            'foods': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def nutrition_info(self, request, pk=None):
        """Get detailed nutrition information for a food"""
        food = self.get_object()
        
        return Response({
            'name': food.name,
            'serving_size': food.serving_size,
            'nutrition_per_serving': {
                'calories': food.calories,
                'protein': food.protein,
                'carbs': food.carbs,
                'fat': food.fat,
                'fiber': food.fiber,
            },
            'nutrition_per_100g': {
                'calories': food.calories,
                'protein': food.protein,
                'carbs': food.carbs,
                'fat': food.fat,
                'fiber': food.fiber,
            }
        })


# ===== USER HEALTH PROFILE VIEWSET =====

class UserHealthProfileViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for UserHealthProfile model.
    Users can only view/edit their own profile.
    """
    serializer_class = UserHealthProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Users can only see their own profile"""
        return UserHealthProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get the user's profile"""
        obj, created = UserHealthProfile.objects.get_or_create(
            user=self.request.user
        )
        return obj
    
    @action(detail=False, methods=['get', 'post'])
    def me(self, request):
        """Get or update the current user's profile"""
        profile, created = UserHealthProfile.objects.get_or_create(
            user=request.user
        )
        
        if request.method == 'POST':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def bmi_info(self, request):
        """Get BMI information and health status"""
        try:
            profile = UserHealthProfile.objects.get(user=request.user)
        except UserHealthProfile.DoesNotExist:
            return Response(
                {'error': 'No health profile found. Please create one first.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        bmi_data = calculate_bmi(profile.weight, profile.height)
        
        return Response({
            'bmi': bmi_data['bmi'],
            'category': bmi_data['category'],
            'health_status': bmi_data['health_status'],
            'weight': profile.weight,
            'height': profile.height,
        })
    
    @action(detail=False, methods=['get'])
    def calorie_requirements(self, request):
        """Get daily calorie requirements"""
        try:
            profile = UserHealthProfile.objects.get(user=request.user)
        except UserHealthProfile.DoesNotExist:
            return Response(
                {'error': 'No health profile found. Please create one first.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        calorie_data = calculate_daily_calorie_requirement(
            profile.age,
            profile.weight,
            profile.height,
            profile.gender,
            profile.activity_level
        )
        
        return Response(calorie_data)
    
    @action(detail=False, methods=['get'])
    def diet_suggestion(self, request):
        """Get diet suggestion based on profile"""
        try:
            profile = UserHealthProfile.objects.get(user=request.user)
        except UserHealthProfile.DoesNotExist:
            return Response(
                {'error': 'No health profile found. Please create one first.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        bmi = calculate_bmi(profile.weight, profile.height)['bmi']
        
        calorie_data = calculate_daily_calorie_requirement(
            profile.age,
            profile.weight,
            profile.height,
            profile.gender,
            profile.activity_level
        )
        
        suggestion = suggest_diet_plan(
            bmi,
            profile.health_goal,
            calorie_data['recommendation']
        )
        
        return Response(suggestion)


# ===== DIET PLAN VIEWSET =====

class DietPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for DietPlan model.
    Read-only access to available diet plans.
    """
    queryset = DietPlan.objects.filter(is_active=True)
    serializer_class = DietPlanSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'diet_type', 'description']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def by_goal(self, request):
        """Get diet plans based on health goal"""
        health_goal = request.query_params.get('goal', None)
        
        if not health_goal:
            return Response(
                {'error': 'Please specify a health goal'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Map health goals to diet types
        goal_diet_mapping = {
            'weight_loss': ['low_carb', 'balanced'],
            'weight_gain': ['high_calorie', 'balanced'],
            'muscle_gain': ['high_protein', 'balanced'],
            'maintenance': ['balanced'],
            'fitness': ['high_protein', 'balanced'],
        }
        
        diet_types = goal_diet_mapping.get(health_goal, ['balanced'])
        plans = DietPlan.objects.filter(
            is_active=True,
            diet_type__in=diet_types
        )
        
        serializer = self.get_serializer(plans, many=True)
        
        return Response({
            'goal': health_goal,
            'recommended_plans': serializer.data
        })


# ===== MEAL VIEWSET =====

class MealViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Meal model.
    Read-only access to published meals.
    """
    queryset = Meal.objects.filter(is_published=True)
    serializer_class = MealSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'meal_type', 'instructions']
    ordering_fields = ['name', 'meal_type', 'preparation_time']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter meals based on query parameters"""
        queryset = Meal.objects.filter(is_published=True)
        
        # Filter by meal type
        meal_type = self.request.query_params.get('meal_type', None)
        if meal_type:
            queryset = queryset.filter(meal_type=meal_type)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Filter by prep time
        max_prep_time = self.request.query_params.get('max_prep_time', None)
        if max_prep_time:
            queryset = queryset.filter(preparation_time__lte=int(max_prep_time))
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get meals filtered by type"""
        meal_type = request.query_params.get('type', None)
        
        if not meal_type:
            return Response(
                {'error': 'Please specify a meal type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        meals = Meal.objects.filter(
            meal_type=meal_type,
            is_published=True
        )
        
        serializer = self.get_serializer(meals, many=True)
        
        return Response({
            'meal_type': meal_type,
            'count': len(meals),
            'meals': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def nutrition_summary(self, request, pk=None):
        """Get nutrition summary for a meal"""
        meal = self.get_object()
        total_macros = meal.get_total_macros()
        
        return Response({
            'meal_name': meal.name,
            'total_calories': meal.get_total_calories(),
            'macros': total_macros,
            'macro_breakdown': {
                'protein': f"{(total_macros['protein'] / (meal.get_total_calories() / 4)) * 100:.1f}%",
                'carbs': f"{(total_macros['carbs'] / (meal.get_total_calories() / 4)) * 100:.1f}%",
                'fat': f"{(total_macros['fat'] / (meal.get_total_calories() / 9)) * 100:.1f}%",
            }
        })


# ===== DAILY LOG VIEWSET =====

class DailyLogViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for DailyLog model.
    Users can only view/create/update their own logs.
    """
    serializer_class = DailyLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        """Users can only see their own logs"""
        return DailyLog.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Automatically set user to current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's log or create if doesn't exist"""
        today = date.today()
        
        log, created = DailyLog.objects.get_or_create(
            user=request.user,
            date=today
        )
        
        serializer = self.get_serializer(log)
        
        return Response({
            'created': created,
            'log': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def this_week(self, request):
        """Get logs for this week"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        logs = self.get_queryset().filter(
            date__gte=week_start,
            date__lte=today
        )
        
        serializer = self.get_serializer(logs, many=True)
        
        return Response({
            'week_start': week_start,
            'week_end': today,
            'logs': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def this_month(self, request):
        """Get logs for this month"""
        today = date.today()
        month_start = today.replace(day=1)
        
        logs = self.get_queryset().filter(
            date__gte=month_start,
            date__lte=today
        )
        
        serializer = self.get_serializer(logs, many=True)
        
        return Response({
            'month_start': month_start,
            'month_end': today,
            'total_days_logged': logs.count(),
            'logs': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        """Get analysis of a daily log"""
        daily_log = self.get_object()
        
        try:
            diet_plan = DietPlan.objects.filter(is_active=True).first()
            if not diet_plan:
                return Response(
                    {'error': 'No active diet plan found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            analysis = analyze_daily_nutrition(daily_log, diet_plan)
            
            return Response(analysis)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
