from django.core.management.base import BaseCommand

from app.financial.models import TagView


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:

            queryset = TagView.objects.filter(client__isnull=True)

            tags_clients = []
            for tag in queryset.order_by('created'):
                tag.client = tag.custom_view.client
                tags_clients.append(tag)
            TagView.objects.bulk_update(tags_clients, fields=["client"])
        except Exception as ex:
            print(f"Error migrate clients tags: {ex}")
