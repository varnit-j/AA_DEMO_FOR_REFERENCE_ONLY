from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/loyalty/', views.loyalty_status, name='loyalty_status'),
    path('api/loyalty/points/add/', views.add_transaction_points, name='add_transaction_points'),
    path('api/loyalty/points/redeem/', views.redeem_points, name='redeem_points'),
    path('api/loyalty/history/<int:user_id>/', views.get_transaction_history, name='get_transaction_history'),
]