import copy
import logging
from django.db.models import Q
from rest_framework import permissions
from app.core.exceptions import WhileListException, InternalTokenInvalidException
from app.core.models import WhileList
from config.settings.common import INTERNAL_TOKEN

logger = logging.getLogger(__name__)


class SafeListPermission(permissions.BasePermission):
    @staticmethod
    def get_ips_addr(request, view):
        user_ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip_address:
            ip_addr = user_ip_address.split(',')[0]
        else:
            ip_addr = request.META.get('REMOTE_ADDR')
        return ip_addr

    def has_permission(self, request, view):
        # validate token internal authorization if catch them in headers request
        token = request.headers.get('authorization')
        if token:
            is_match = (token == INTERNAL_TOKEN)
            if not is_match:
                raise InternalTokenInvalidException(verbose=True)
            return is_match
        # validate ip address in while list
        ip = self.get_ips_addr(request, view)
        is_accepted = WhileList.objects.filter(enabled=True, ip_addr=ip).exists()
        if not is_accepted:
            remote_host = request.META.get('REMOTE_HOST')
            logger.error(f"[{self.__class__.__name__}][has_permission] Remote Host = {remote_host}, "
                         f"Ip Addr {ip} not accept")
            raise WhileListException(verbose=True)
        return is_accepted
