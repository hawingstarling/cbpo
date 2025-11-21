import logging
from django.db import transaction
from django.db.models import Q, F
from rest_framework import serializers
from app.core.context import AppContext
from app.core.exceptions import CustomViewUniqueException
from app.core.sub_serializers.base_serializer import BaseSerializer
from app.financial.variable.variant_type_static_variable import SHARE_PERMISSION_TYPE, SHARE_MODE_TYPE, PRIVATE_MODE, \
    PUBLIC_MODE
from .alert_serializer import AlertSerializer
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from .user_serializer import UserSerializer
from ..models import CustomFilter, CustomColumn, CustomObject, CustomReport, CustomView, ShareCustom, User, \
    TagView, TagUserTrack, TagClient
from rest_framework.fields import empty
from app.financial.services.utils.helper import bulk_sync
from ...core.sub_serializers.custom_field_serializer import ArrayUUIDField

logger = logging.getLogger(__name__)


class ClientTagUserSerializer(TenantDBForSerializer):
    class Meta:
        model = TagUserTrack
        fields = '__all__'

    def bulk_sync(self, validated_data: [dict]):
        objs = []
        for item in validated_data:
            try:
                obj = TagClient.objects.tenant_db_for(self.client_id).get(pk=item['tag_id'], client_id=self.client_id)
                objs.append(TagUserTrack(tag=obj, user_id=self.user_request_id, client_id=self.client_id,
                                         is_widget_default=item["is_widget_default"]))
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}][bulk_sync] {ex}")
        bulk_sync(
            client_id=self.client_id,
            new_models=objs,
            filters=Q(client_id=self.client_id, user_id=self.user_request_id),
            key_fields=['client', 'tag', 'user'],
            fields=['client', 'tag', 'user', "is_widget_default"]
        )


class ClientTagViewSerializer(TenantDBForSerializer):
    class Meta:
        model = TagView
        fields = '__all__'


class CustomColumnCreateSerializer(BaseSerializer):
    name = serializers.CharField(max_length=200, required=True)
    ds_column = serializers.JSONField(required=True)
    ds_config = serializers.JSONField(required=False)
    share_mode = serializers.IntegerField(default=0)
    featured = serializers.BooleanField(default=False)


class CustomFilterCreateSerializer(BaseSerializer):
    name = serializers.CharField(max_length=200, required=True)
    ds_filter = serializers.JSONField(required=True)
    ds_config = serializers.JSONField(required=False)
    share_mode = serializers.IntegerField(default=0)
    featured = serializers.BooleanField(default=False)


class CustomViewCreateSerializer(BaseSerializer):
    name = serializers.CharField(max_length=200, required=True)
    ds_column = serializers.JSONField(required=True)
    ds_filter = serializers.JSONField(required=True)
    ds_config = serializers.JSONField(required=False)
    share_mode = serializers.IntegerField(default=0)
    featured = serializers.BooleanField(default=False)
    tags = serializers.ListField(required=False, child=serializers.UUIDField())


class CustomTypeBaseSerializer(TenantDBForSerializer):
    is_shared = serializers.SerializerMethodField()
    permission = serializers.SerializerMethodField()
    user_info = serializers.SerializerMethodField()
    featured = serializers.BooleanField(default=False)

    class Meta:
        model = None
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'user_id': {'required': False},
            'client': {'required': False},
            'created': {'read_only': True},
            'modified': {'read_only': True},
            'is_removed': {'required': False}
        }

    def get_unique_together_validators(self):
        return []

    def create(self, validated_data):
        featured = None
        if 'featured' in validated_data:
            featured = validated_data.pop('featured')
        client_id = AppContext.instance().client_id
        query_set = self.Meta.model.all_objects.tenant_db_for(client_id).filter(name=validated_data['name'],
                                                                                client_id=client_id, is_removed=True)
        find = query_set.first()
        if query_set.exists():
            query_set.filter(pk=find.pk).update(**validated_data, is_removed=False)
            find.refresh_from_db()
            # favorite user
            self.process_favorite_object_user(find, featured)
            return find
        instance = super().create(validated_data)
        # favorite user
        self.process_favorite_object_user(instance, featured)
        return instance

    def update(self, instance, validated_data):
        featured = None
        if 'featured' in validated_data:
            featured = validated_data.pop('featured')
        validated_data.update({'user': instance.user})
        instance = super().update(instance, validated_data)
        # favorite user
        self.process_favorite_object_user(instance, featured)
        return instance

    @staticmethod
    def process_favorite_object_user(instance, featured):
        #
        if featured is not None:
            client_id = AppContext.instance().client_id
            user_id = AppContext.instance().user_id
            instance.favorites.update_or_create(client_id=client_id, user_id=user_id,
                                                defaults={'status': featured})

    def validate_name(self, name):
        # instance current
        client_id = AppContext.instance().client_id
        instance = self.instance
        obj = self.Meta.model.objects.tenant_db_for(client_id).filter(name=name, client_id=client_id).first()
        conditions = not obj or (instance and str(instance.pk) == str(obj.pk))
        if conditions:
            return name
        raise CustomViewUniqueException(viewname=name)

    def get_is_shared(self, obj):
        user_email = AppContext.instance().user_email
        share = obj.share_users.filter(user_email=user_email)
        return share.exists()

    def get_permission(self, obj):
        user_email = AppContext.instance().user_email
        share = obj.share_users.filter(user_email=user_email).first()
        return share.permission if share else SHARE_PERMISSION_TYPE[1][0]

    def get_user_info(self, obj):
        try:
            user = User.objects.tenant_db_for(obj.client_id).get(user_id=obj.user_id)
            return UserSerializer(user).data
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}] {ex}")
            return {}

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        try:
            user_id = AppContext.instance().user_id
            ret.update({'featured': instance.favorites.get(user_id=user_id).status})
        except Exception:
            pass
        return ret


class CustomFilterSerializer(CustomTypeBaseSerializer):
    class Meta(CustomTypeBaseSerializer.Meta):
        model = CustomFilter


class CustomColumnSerializer(CustomTypeBaseSerializer):
    class Meta(CustomTypeBaseSerializer.Meta):
        model = CustomColumn


class ClientTagViewWidgetDefaultSerializer(BaseSerializer):
    tag_id = serializers.UUIDField(required=True)
    is_widget_default = serializers.BooleanField(required=True)


class ClientTagViewWidgetPayloadSerializer(BaseSerializer):
    tags = ClientTagViewWidgetDefaultSerializer(many=True, required=True)


class CustomViewSerializer(CustomTypeBaseSerializer):
    alert_info = AlertSerializer(many=True, read_only=True)
    tags = serializers.ListField(required=False, child=serializers.UUIDField())

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.tags = []
        self.is_tags_changes = False

    class Meta(CustomTypeBaseSerializer.Meta):
        model = CustomView

    def prefetch_tags(self, validated_data):
        if 'tags' in validated_data:
            self.is_tags_changes = True
            self.tags = validated_data.pop('tags')

    def sync_tags_view(self, ins):
        try:
            if not self.is_tags_changes:
                return
            for tag_id in self.tags:
                TagView.objects.get_or_create(client_id=self.client_id, custom_view=ins, tag_id=tag_id)
            queryset = TagView.objects.filter(client_id=self.client_id, custom_view=ins)
            if self.tags:
                queryset.exclude(tag_id__in=self.tags).delete()
            else:
                queryset.delete()
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}] {ex}")

    def create(self, validated_data):
        self.prefetch_tags(validated_data)
        ins = super().create(validated_data)
        transaction.on_commit(lambda: self.sync_tags_view(ins))
        return ins

    def update(self, instance, validated_data):
        self.prefetch_tags(validated_data)
        ins = super().update(instance, validated_data)
        transaction.on_commit(lambda: self.sync_tags_view(ins))
        return ins

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if len(data.get('alert_info', [])) > 0:
            data.update({'alert_info': data['alert_info'][0]})
        if self.fields == 'all' or 'tags' in self.fields:
            tags_data = instance.tagview_set.annotate(tag_name=F('tag__name'), tag_color=F('tag__color')) \
                .values('tag_id', 'tag_name', 'tag_color')
            data.update({'tags': tags_data})
        return data


class CustomViewDropdownSerializer(CustomViewSerializer):
    class Meta(CustomViewSerializer.Meta):
        fields = ['id', 'name', 'user_info']


class CustomViewTagFiltersSerializer(CustomViewSerializer):
    class Meta(CustomViewSerializer.Meta):
        fields = ['name', 'ds_filter']


class CustomReportSerializer(CustomTypeBaseSerializer):
    item_ids = ArrayUUIDField(child=serializers.UUIDField(), required=False)
    ds_query = serializers.JSONField(required=False)
    columns = serializers.JSONField(required=False)
    bulk_operations = serializers.JSONField(required=False)

    class Meta(CustomTypeBaseSerializer.Meta):
        model = CustomReport
        fields = [i.name for i in model._meta.fields]

    def create(self, validated_data):
        return CustomReport.objects.tenant_db_for(self.client_id).create(**validated_data)


class CustomReportCreateSerializer(CustomReportSerializer):
    class Meta(CustomReportSerializer.Meta):
        fields = ['name', 'item_ids', 'ds_query', 'columns', 'bulk_operations', 'share_mode', 'featured']


class BulkOperatorShippingInvoiceCRSerializer(BaseSerializer):
    column = serializers.CharField()
    value = serializers.CharField()


class CustomReportSlugCreateSerializer(CustomReportCreateSerializer):
    item_ids = ArrayUUIDField(child=serializers.UUIDField(), required=False)
    bulk_operations = serializers.ListField(child=BulkOperatorShippingInvoiceCRSerializer())

    class Meta(CustomReportCreateSerializer.Meta):
        fields = ['item_ids', 'bulk_operations']


# share custom serializer collections
class ShareUserInfoView(BaseSerializer):
    user_email = serializers.EmailField()
    permission = serializers.ChoiceField(choices=SHARE_PERMISSION_TYPE)


class ShareCustomSerializer(TenantDBForSerializer):
    share_mode = serializers.ChoiceField(choices=SHARE_MODE_TYPE, required=True)
    shared_users = serializers.ListField(child=ShareUserInfoView(), required=True)

    class Meta:
        model = ShareCustom
        fields = ('share_mode', 'shared_users',)

    def update(self, instance, validated_data):
        # shared mode
        share_mode = validated_data.get('share_mode', None)
        if share_mode in [PRIVATE_MODE, PUBLIC_MODE]:
            instance.share_mode = share_mode
            instance.save()
        client = self.context.get('client')
        self.sync_share_users(instance, client, validated_data)

    def sync_share_users(self, obj, client, validated_data):
        share_custom_created: list = []
        share_custom_updated: list = []
        user_email_list: list = []
        client_id = str(client.pk)
        for item in validated_data.get('shared_users', []):
            user_email_list.append(item['user_email'])
            obj_share = ShareCustom.all_objects.tenant_db_for(client_id).filter(client=client,
                                                                                user_email=item['user_email'],
                                                                                object_id=obj.pk).first()
            if obj_share:
                obj_share.permission = item['permission']
                obj_share.is_removed = False
                share_custom_updated.append(obj_share)
                continue
            obj_share = ShareCustom(client=client, user_email=item['user_email'],
                                    content_object=obj,
                                    permission=item['permission'])
            share_custom_created.append(obj_share)
        ShareCustom.objects.tenant_db_for(client_id).bulk_create(objs=share_custom_created)
        ShareCustom.all_objects.tenant_db_for(client_id).bulk_update(objs=share_custom_updated,
                                                                     fields=['permission', 'is_removed'])
        # remove share custom with list email not exist
        condition_remove = Q(object_id=str(obj.pk)) & ~Q(user_email__in=user_email_list)
        ShareCustom.objects.tenant_db_for(client_id).filter(condition_remove).delete()


class ShareCustomListSerializer(ShareCustomSerializer):
    user_info = serializers.SerializerMethodField()

    class Meta(ShareCustomSerializer.Meta):
        fields = ('user_email', 'user_info', 'permission')

    def get_user_info(self, obj):
        try:
            user = User.objects.tenant_db_for(obj.client_id).get(user_email=obj.user_email)
            return UserSerializer(user).data
        except Exception as ex:
            return {}


class CustomObjectSerializer(TenantDBForSerializer):
    content = serializers.JSONField(required=True)

    def create(self, validated_data):
        client = validated_data['client']
        hash_content = validated_data['hash_content']
        instance, _ = CustomObject.objects.tenant_db_for(client.id).get_or_create(client=client,
                                                                                  hash_content=hash_content,
                                                                                  defaults=validated_data)
        return instance

    class Meta:
        model = CustomObject
        fields = '__all__'
        read_only_fields = ['hash_content']
