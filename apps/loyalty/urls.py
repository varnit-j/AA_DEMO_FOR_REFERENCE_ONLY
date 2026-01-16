from django.urls import path
from . import views

app_name = 'loyalty'

urlpatterns = [
    path('dashboard/', views.loyalty_dashboard, name='dashboard'),
    path('points-history/', views.points_history, name='points_history'),
    path('tier-info/', views.tier_info, name='tier_info'),
    path('api/calculate-points-value/', views.calculate_points_value, name='calculate_points_value'),
]