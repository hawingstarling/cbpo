from django.urls import path

from app.app_setting import views

urlpatterns = [
    path(
        "<str:app_id>/lwa-client-setting",
        views.RetrieLWACredentialSettingView.as_view(),
        name="retrieve-lwa-credential",
    )
]
