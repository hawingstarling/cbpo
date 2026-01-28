from django.db import transaction

from .controller import ImportController
from ...static_variable.config import plat_import_setting
from ...tasks import lib_import_process_action_task


class ImportJobManager(ImportController):

    def process(self):
        if plat_import_setting.use_queue:
            transaction.on_commit(
                lambda: lib_import_process_action_task.delay(lib_import_id=self.lib_import_id, action=self.action,
                                                             map_config_request=self.map_config_request))

        else:
            lib_import_process_action_task(lib_import_id=self.lib_import_id, action=self.action,
                                           map_config_request=self.map_config_request)
