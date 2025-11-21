from .sub_urls import client
from .sub_urls import organization

urlpatterns = client.urlpatterns + organization.urlpatterns
