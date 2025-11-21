from rest_framework.fields import ListField


class ArrayUUIDField(ListField):
    """
    ArrayUUIDField
    """

    def to_internal_value(self, data):
        if data:
            data = list(set(map(lambda x: str(x), data)))
        return super().to_internal_value(data)
