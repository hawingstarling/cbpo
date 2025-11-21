from rest_framework import serializers

from app.tenancies.models import User


class UserCommonSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name']
