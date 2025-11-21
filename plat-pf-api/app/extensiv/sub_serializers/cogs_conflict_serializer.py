from rest_framework import serializers

from app.extensiv.models import COGSConflict


class ExtensivCOGsConflictSerializer(serializers.ModelSerializer):
    class Meta:
        model = COGSConflict
        fields = '__all__'
