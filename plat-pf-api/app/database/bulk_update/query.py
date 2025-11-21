from django.db import models
from django_bulk_update.helper import bulk_update


class BulkUpdateQuerySet(models.QuerySet):

    def bulk_update(self, objs, fields=None,
                    excludes=None, batch_size=None):
        self._for_write = True
        using = self.db

        return bulk_update(
            objs, update_fields=fields,
            exclude_fields=excludes, using=using,
            batch_size=batch_size)
