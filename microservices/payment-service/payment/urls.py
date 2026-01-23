from django.contrib import admin
from django.urls import path, include
from . import views, saga_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/payments/process/', views.process_payment, name='process_payment'),
    path('api/payments/stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('api/payments/<str:payment_id>/', views.payment_status, name='payment_status'),
    path('api/payments/refund/', views.process_refund, name='process_refund'),
    path('api/banking/validate/', views.validate_card, name='validate_card'),
    path('health/', views.health_check, name='health_check'),
    
    # SAGA endpoints
    path('api/saga/authorize-payment/', saga_views.authorize_payment, name='saga_authorize_payment'),
    path('api/saga/cancel-payment/', saga_views.cancel_payment, name='saga_cancel_payment'),
]