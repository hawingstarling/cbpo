from django.contrib.admin import SimpleListFilter


class GlobalChannelListFilter(SimpleListFilter):
    title = 'channel'
    parameter_name = 'channel'

    def lookups(self, request, model_admin):
        from app.financial.models import Channel  # Adjust import
        active_channels = Channel.objects.filter(use_in_global_filter=True)
        return [(c.id, c.name) for c in active_channels]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(channel_id=self.value())
        return queryset
