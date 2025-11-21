from distutils.util import strtobool
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, FilteredRelation, F
from django.db.models.functions import Coalesce
from app.core.context import AppContext
from app.core.services.authentication_service import AuthenticationService
from app.core.services.user_permission import get_user_permission
from app.financial.models import CustomReport, ShareCustom, CustomColumn, CustomFilter, CustomView
from app.database.helper import get_connection_workspace
from app.financial.variable.variant_type_static_variable import PUBLIC_MODE, EDIT_PERMISSION
from app.core.variable.permission import ROLE_OWNER

custom_object_column_key = {
    CustomColumn: 'COLUMN',
    CustomFilter: 'FILTER',
    CustomView: 'REPORT',
    CustomReport: 'VIEW',
}


class CustomViewService:

    def __init__(self, content_type_id: int, user_id: str):

        self.content_type_id = content_type_id
        self.user_id = str(user_id)

        # get ws from app context
        self.client_id = AppContext.instance().client_id
        self.jwt_token = AppContext.instance().jwt_token
        self.user_email = AuthenticationService.get_email_jwt_token(jwt_token=self.jwt_token)

        # get model class by content type id
        self.model_class = self.get_model_class()

        # load info permissions from portal
        self.user_permission = get_user_permission(self.jwt_token, self.client_id, self.user_id)
        self.permissions = self.user_permission.permissions
        self.role = self.user_permission.role

    def __has_permission_workspace(self, name):
        column_key = custom_object_column_key.get(self.model_class, None)
        key = f"{name}_{column_key}"
        permission = self.permissions.get(key, False)
        return permission

    def get_model_class(self):
        client_db = get_connection_workspace(self.client_id)
        model_class = ContentType.objects.db_manager(using=client_db).get(id=self.content_type_id).model_class()
        return model_class

    @property
    def __has_view_permission_group(self):
        key = 'SALE_REPORT_VIEW'
        if self.model_class == CustomView:
            key = 'SALE_REPORT_VIEW_ALL'
        elif self.model_class == CustomReport:
            key = 'PF_CUSTOM_REPORT'
        return bool(self.__has_permission_workspace(key))

    def get_query_set_my_custom_obj(self, filter_type: str = "all", search: str = None, featured=None,
                                    is_load_favorites: bool = True):
        cond = Q(client_id=self.client_id)
        if filter_type == 'shared':
            # get all custom share
            cond &= Q(share_users__user_email=self.user_email)
        elif filter_type == 'myself':
            # get all custom myself
            cond &= Q(user_id=self.user_id)
        else:
            # get all custom share
            cond_public = None
            if self.__has_view_permission_group:
                cond_public = Q(share_mode=PUBLIC_MODE)
            # get all objects myself mode
            cond_myself = Q(user_id=self.user_id)
            # get all custom share
            cond_shared = Q(share_users__user_email=self.user_email)
            if cond_public:
                cond &= (cond_public | cond_myself | cond_shared)
            else:
                cond &= (cond_myself | cond_shared)

        if search:
            cond &= Q(name__icontains=search)

        query_set = self.model_class.objects.tenant_db_for(self.client_id).filter(cond)
        if is_load_favorites:
            query_set = query_set.annotate(
                favorites_user=FilteredRelation('favorites', condition=Q(favorites__user_id=self.user_id)),
                featured=Coalesce(F('favorites_user__status'), False)
            )
        #
        if featured is not None:
            query_set = query_set.filter(featured=bool(strtobool(featured)))
        return query_set.distinct()

    def get_query_set_share_custom(self, object_id: str = None, user_email: str = None, filters: dict = {}):
        query_set = ShareCustom.objects.tenant_db_for(self.client_id).filter(content_type__pk=self.content_type_id,
                                                                             client_id=self.client_id)
        #
        if object_id:
            query_set = query_set.filter(object_id=object_id)
        #
        if user_email:
            query_set = query_set.filter(user_email=user_email)
        #
        if filters:
            query_set = query_set.filter(**filters)
        return query_set

    def get_custom_obj(self, object_id: str):
        return self.model_class.objects.tenant_db_for(self.client_id).get(id=object_id)

    def has_share_mode_custom_obj(self, object_id: str):
        obj = self.get_custom_obj(object_id=object_id)
        return obj.share_mode

    def has_manage_model_custom_obj(self, object_id: str):
        obj = self.get_custom_obj(object_id=object_id)

        # accept all user edit if objects is public mode
        key = 'SALE_REPORT_EDIT'
        if obj.share_mode == PUBLIC_MODE and self.__has_permission_workspace(key):
            return True
        # if private mode (check user email shared mode EDIT)
        shared_obj = obj.share_users.tenant_db_for(self.client_id).filter(user_email=self.user_email,
                                                                          permission=EDIT_PERMISSION)

        return str(obj.user_id) == self.user_id or shared_obj.exists()

    def has_delete_model_custom_obj(self, object_id: str):
        # delete accept onwer role or creator
        #
        obj = self.get_custom_obj(object_id=object_id)
        return str(obj.user_id) == self.user_id or self.role == ROLE_OWNER

    def has_view_model_custom_obj(self, object_id: str = None):
        obj = self.get_custom_obj(object_id=object_id)
        if obj.share_mode == PUBLIC_MODE and self.__has_view_permission_group:
            return True
        user_email = AppContext.instance().user_email
        shared_obj = obj.share_users.filter(user_email=user_email)
        return str(obj.user_id) == self.user_id or shared_obj.exists()

    def has_share_mode_custom_obj(self, object_id: str):
        obj = self.get_custom_obj(object_id=object_id)
        # accept all user share if objects is public mode
        key = 'SALE_REPORT_SHARE'
        if obj.share_mode == PUBLIC_MODE and self.__has_permission_workspace(key):
            return True
        return str(obj.user_id) == self.user_id
