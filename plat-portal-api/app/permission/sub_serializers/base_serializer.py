from rest_framework import serializers

from app.permission.models import OrgClientCustomRoleUser


class BaseSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class OrgClientCustomRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgClientCustomRoleUser
        fields = '__all__'


class OrgClientRoleConfigSerializer(OrgClientCustomRoleSerializer):
    id = serializers.SerializerMethodField(method_name='get_custom_role_id')
    name = serializers.SerializerMethodField(method_name='get_custom_role_name')

    class Meta(OrgClientCustomRoleSerializer.Meta):
        fields = ('id', 'name', 'priority',)

    def get_custom_role_id(self, instance):
        return str(instance.custom_role.id)

    def get_custom_role_name(self, instance):
        return instance.custom_role.name
