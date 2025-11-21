from app.core.exceptions import InvalidShareCustomException
from app.financial.permissions.base import ClientUserPermission, JwtTokenPermission
from app.database.helper import get_connection_workspace
from app.financial.services.custom_views import CustomViewService
from django.contrib.contenttypes.models import ContentType


class ShareModePermission(JwtTokenPermission):

    def has_permission(self, request, view):
        super().has_permission(request, view)
        obj_id = view.kwargs.get('pk', None)
        custom_model = view.custom_model
        user_id = str(view.kwargs.get('user_id'))
        client_id = str(view.kwargs.get('client_id'))
        client_db = get_connection_workspace(client_id)
        content_type_id = ContentType.objects.db_manager(using=client_db).get_for_model(custom_model).pk
        custom_service = CustomViewService(content_type_id=content_type_id, user_id=user_id)
        share_mode = custom_service.has_share_mode_custom_obj(object_id=obj_id)
        if not share_mode:
            raise InvalidShareCustomException(message="You don't have share permission")
        return True


class CustomTypeViewPermission(ClientUserPermission):
    def has_permission(self, request, view):
        super().has_permission(request, view)
        obj_id = view.kwargs.get('pk', None)
        user_id = view.kwargs.get('user_id', None)
        custom_model = view.custom_model
        client_id = str(view.kwargs.get('client_id'))
        client_db = get_connection_workspace(client_id)
        content_type_id = ContentType.objects.db_manager(using=client_db).get_for_model(custom_model).pk
        custom_service = CustomViewService(content_type_id=content_type_id, user_id=user_id)
        view_mode = custom_service.has_view_model_custom_obj(object_id=str(obj_id))
        if not view_mode:
            raise InvalidShareCustomException(message="You don't have permission view")
        return True


class CustomTypeUpdatePermission(ClientUserPermission):
    def has_permission(self, request, view):
        super().has_permission(request, view)
        obj_id = view.kwargs.get('pk')
        user_id = view.kwargs.get('user_id')
        custom_model = view.custom_model
        client_id = str(view.kwargs.get('client_id'))
        client_db = get_connection_workspace(client_id)
        content_type_id = ContentType.objects.db_manager(using=client_db).get_for_model(custom_model).pk
        custom_service = CustomViewService(content_type_id=content_type_id, user_id=user_id)
        share_mode = custom_service.has_manage_model_custom_obj(object_id=str(obj_id))
        if not share_mode:
            raise InvalidShareCustomException(message="You can't permission edit")
        return True


class CustomTypeDeletePermission(ClientUserPermission):
    def has_permission(self, request, view):
        super().has_permission(request, view)
        obj_id = view.kwargs.get('pk')
        user_id = view.kwargs.get('user_id')
        custom_model = view.custom_model
        client_id = str(view.kwargs.get('client_id'))
        client_db = get_connection_workspace(client_id)
        content_type_id = ContentType.objects.db_manager(using=client_db).get_for_model(custom_model).pk
        custom_service = CustomViewService(content_type_id=content_type_id, user_id=user_id)
        share_mode = custom_service.has_delete_model_custom_obj(object_id=str(obj_id))
        if not share_mode:
            raise InvalidShareCustomException(message="You can't permission delete")
        return True
