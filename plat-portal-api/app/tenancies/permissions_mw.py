from rest_framework.permissions import AllowAny
from app.core.services_authentication import MWJSONWebTokenAuthentication


class IsMWServices(AllowAny):
    def has_permission(self, request, view):
        MWJSONWebTokenAuthentication().authenticate(request=request)
        return True
