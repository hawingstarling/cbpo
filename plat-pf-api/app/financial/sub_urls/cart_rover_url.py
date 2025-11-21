from django.urls import path
from app.financial.sub_views.client_settings_view import ClientCartRoverValidationView

urlpatterns = [
    path('clients/<uuid:client_id>/cart-rover/validation', ClientCartRoverValidationView.as_view(),
         name='client-cart-rover-validation')
]
