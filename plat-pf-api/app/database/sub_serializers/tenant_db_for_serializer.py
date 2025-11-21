from rest_framework import serializers
from rest_framework.fields import empty
from app.core.context import AppContext
from app.database.helper import get_connection_workspace


class TenantDBForSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = '__all__'

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        try:
            view = self.context.get('view', {})
            self.client_id = view.kwargs['client_id']
        except Exception as ex:
            kwargs = self.context.get('kwargs', {})
            self.client_id = kwargs.get('client_id', AppContext.instance().client_id)
        #
        self.client_db = get_connection_workspace(self.client_id)
        self.user_request_id = AppContext.instance().user_id
        #
        try:
            self.Meta.model.objects.tenant_db_for(self.client_id)
        except Exception as ex:
            self.Meta.model.objects._db = self.client_db
        #

    def create(self, validated_data):
        if hasattr(self.Meta.model, 'all_objects'):
            model_manage = self.Meta.model.all_objects
        else:
            model_manage = self.Meta.model.objects
        return model_manage.db_manager(using=self.client_db).create(**validated_data)

    def update(self, instance, validated_data):
        instance._state.db = self.client_db
        return super().update(instance, validated_data)
