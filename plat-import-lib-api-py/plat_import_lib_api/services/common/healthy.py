import datetime
import logging
from django.utils import timezone
from ...models import DataImportTemporary, Health
from ...static_variable.config import plat_import_setting

logger = logging.getLogger(__name__)


class HealthyModule:
    def __init__(self, module: str):
        self.module = module
        self.total = 0
        self.healthy_module = None

    def validate(self):
        self.healthy_module, _ = Health.objects.get_or_create(module_name=self.module)
        assert self.healthy_module.is_enabled is True, "module name disabled check healthy"

    def process(self):
        logger.info(f"[{self.__class__.__name__}][{self.module}][process] Begin")
        try:
            time_late_limit = timezone.now() - datetime.timedelta(minutes=plat_import_setting.healthy_check_minute)
            queryset = DataImportTemporary.objects.filter(module=self.module, progress__lt=100,
                                                          modified__lt=time_late_limit)
            self.total = queryset.count()
            self.healthy_module.is_healthy = self.total == 0
            self.healthy_module.message = f"{self.total} records not running " if not self.healthy_module.is_healthy else "OK"
            self.healthy_module.client_ids = list(queryset.values_list('client_id', flat=True).distinct())
            self.healthy_module.import_ids = list(queryset.values_list('id', flat=True))
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][process] {ex}")

    def complete(self):
        self.healthy_module.save()
