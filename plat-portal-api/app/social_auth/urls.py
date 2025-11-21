from django.urls import path, include

from app.social_auth.views import GoogleLoginView

urlpatterns = [
    path('accounts/', include('allauth.urls'), name='socialaccount_signup'),
    path('google/', GoogleLoginView.as_view(), name='google-login'),
]
