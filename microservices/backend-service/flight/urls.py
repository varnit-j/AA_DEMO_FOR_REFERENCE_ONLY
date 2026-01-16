from django.urls import path
from . import simple_views

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
    path('tickets/<str:booking_ref>/update_status/', simple_views.update_ticket_status, name='update_ticket_status'),
]