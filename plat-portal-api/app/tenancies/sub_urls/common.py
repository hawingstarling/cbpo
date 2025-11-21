from django.urls import path

from ..sub_views.common import ImageUploadView

urlpatterns = [
    path('upload/', ImageUploadView.as_view(),
         name='upload-image')
]
