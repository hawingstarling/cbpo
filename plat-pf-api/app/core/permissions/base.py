from rest_framework.permissions import BasePermission

from app.core.exceptions import InternalTokenRequiredException
from config.settings.common import INTERNAL_TOKEN


class InternalPermission(BasePermission):
    def has_permission(self, request, view):
        token = request.headers.get('authorization')
        if not token:
            raise InternalTokenRequiredException()
        return token == INTERNAL_TOKEN
