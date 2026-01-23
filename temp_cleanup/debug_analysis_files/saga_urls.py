"""
SAGA URL Configuration for Backend Service
"""
from django.urls import path
from . import saga_views

urlpatterns = [
    # SAGA Action endpoints
    path('api/saga/reserve-seat/', saga_views.reserve_seat, name='saga_reserve_seat'),
    path('api/saga/confirm-booking/', saga_views.confirm_booking, name='saga_confirm_booking'),
    
    # SAGA Compensation endpoints
    path('api/saga/cancel-seat/', saga_views.cancel_seat, name='saga_cancel_seat'),
    path('api/saga/cancel-booking/', saga_views.cancel_booking, name='saga_cancel_booking'),
    
    # SAGA Management endpoints
    path('api/saga/start-booking/', saga_views.start_booking_saga, name='saga_start_booking'),
    path('api/saga/status/<str:correlation_id>/', saga_views.get_saga_status, name='saga_status'),
]