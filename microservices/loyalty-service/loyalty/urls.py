from django.contrib import admin
from django.urls import path
from . import views, saga_views

from . import saga_views

urlpatterns = [
    path('award-miles/', saga_views.award_miles, name='award_miles'),
    path('reverse-miles/', saga_views.reverse_miles, name='reverse_miles'),
    path('admin/', admin.site.urls),
    
    # Main loyalty endpoints
    path('loyalty/status/', views.loyalty_status, name='loyalty_status'),
    path('loyalty/add-points/', views.add_transaction_points, name='add_transaction_points'),
    path('loyalty/redeem-points/', views.redeem_points, name='redeem_points'),
    path('loyalty/transactions/<str:user_id>/', views.get_transaction_history, name='get_transaction_history'),
    
    # Legacy API endpoints (for backward compatibility)
    path('api/loyalty/', views.loyalty_status, name='legacy_loyalty_status'),
    path('api/loyalty/points/add/', views.add_transaction_points, name='legacy_add_transaction_points'),
    path('api/loyalty/points/redeem/', views.redeem_points, name='legacy_redeem_points'),
    path('api/loyalty/history/<str:user_id>/', views.get_transaction_history, name='legacy_get_transaction_history'),
    
    # SAGA endpoints
    path('api/saga/award-miles/', saga_views.award_miles, name='saga_award_miles'),
    path('api/saga/reverse-miles/', saga_views.reverse_miles, name='saga_reverse_miles'),
]