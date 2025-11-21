from rest_framework.serializers import ModelSerializer

from app.payments.models import (
    MapWatcherConfig,
)


class MapWatcherConfigSerializer(ModelSerializer):
    class Meta:
        model = MapWatcherConfig
        exclude = (
            "id",
            "created",
            "modified",
        )
