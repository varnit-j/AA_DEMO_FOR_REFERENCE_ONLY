from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/payments/process/', views.process_payment, name='process_payment'),
    path('api/payments/stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('api/payments/<str:payment_id>/', views.payment_status, name='payment_status'),
    path('api/payments/refund/', views.process_refund, name='process_refund'),
    path('api/banking/validate/', views.validate_card, name='validate_card'),
    path('health/', views.health_check, name='health_check'),
]