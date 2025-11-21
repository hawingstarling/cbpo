from rest_framework.permissions import AllowAny

from app.core.services_authentication import InternalJSONWebTokenAuthentication


class IsInternalServices(AllowAny):
    def has_permission(self, request, view):
        InternalJSONWebTokenAuthentication().authenticate(request=request)
        return True
