from rest_framework.permissions import AllowAny
from app.core.services_authentication import DTDJSONWebTokenAuthentication


class IsDTDServices(AllowAny):
    def has_permission(self, request, view):
        DTDJSONWebTokenAuthentication().authenticate(request=request)
        return True
