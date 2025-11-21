from rest_framework.validators import UniqueTogetherValidator
from app.core.context import AppContext
from app.financial.models import AppEagleProfile
from app.financial.sub_serializers.default_message_serializer import default_error_message
from django.utils.translation import gettext_lazy as _
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer


class AppEagleProfileSerializer(TenantDBForSerializer):
    class Meta:
        model = AppEagleProfile
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=AppEagleProfile.objects.tenant_db_for(AppContext.instance().client_id).all(),
                fields=['client', 'profile_id'],
                message=_('Profile ID must be unique')
            )
        ]


class AppEagleProfileImportSerializer(AppEagleProfileSerializer):
    class Meta:
        model = AppEagleProfile
        fields = ['profile_id', 'profile_name']

        extra_kwargs = {
            'profile_id': {
                "error_messages": default_error_message('Profile ID'),
                "label": 'Profile ID'
            },
            'profile_name': {
                "error_messages": default_error_message('Profile Name'),
                "label": 'Profile Name'
            }
        }
