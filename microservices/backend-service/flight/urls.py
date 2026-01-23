from django.urls import path
from . import simple_views

# Import SAGA views
try:
    from . import saga_views_complete
    SAGA_AVAILABLE = True
except ImportError:
    SAGA_AVAILABLE = False

urlpatterns = [
    # Health check
    path('health/', simple_views.health_check, name='health_check'),
    
    # Places
    path('places/search/', simple_views.places_search, name='places_search'),
    
    # Flights
    path('flights/search/', simple_views.flight_search, name='flight_search'),
    path('flights/<int:flight_id>/', simple_views.get_flight_detail, name='flight_detail'),
    path('flights/book/', simple_views.book_flight, name='book_flight'),
    
    # Tickets
    path('tickets/user/<int:user_id>/', simple_views.get_user_tickets, name='get_user_tickets'),
    path('tickets/user/<int:user_id>/with-saga/', simple_views.get_user_tickets_with_saga, name='get_user_tickets_with_saga'),
    path('tickets/<str:booking_ref>/update_status/', simple_views.update_ticket_status, name='update_ticket_status'),
]

# Add SAGA endpoints if available
if SAGA_AVAILABLE:
    urlpatterns += [
        # SAGA Action endpoints
        path('saga/reserve-seat/', saga_views_complete.reserve_seat, name='saga_reserve_seat'),
        path('saga/confirm-booking/', saga_views_complete.confirm_booking, name='saga_confirm_booking'),
        path('saga/start-booking/', saga_views_complete.start_booking_saga, name='saga_start_booking'),
        
        # SAGA Compensation endpoints
        path('saga/cancel-seat/', saga_views_complete.cancel_seat, name='saga_cancel_seat'),
        path('saga/cancel-booking/', saga_views_complete.cancel_booking, name='saga_cancel_booking'),
        
        # SAGA Management endpoints
        path('saga/status/<str:correlation_id>/', saga_views_complete.get_saga_status, name='saga_status'),
        path('saga/logs/<str:correlation_id>/', saga_views_complete.get_saga_logs, name='saga_logs'),
        path('saga/demo-failure/', saga_views_complete.demo_saga_failure, name='saga_demo_failure'),
    ]