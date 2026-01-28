import importlib
import logging
from ...static_variable.config import plat_import_setting
from ...services.utils.exceptions import InvalidModuleException

logger = logging.getLogger(__name__)


class ModuleImportService(object):

    def __init__(self, name: str, **kwargs):
        assert name is not None, f"[{self.__class__.__name__}] Module name is not none"
        self.module = name
        self.kwargs = kwargs

    def get_module_define(self):
        # Get setting from environment
        try:
            modules = importlib.import_module(plat_import_setting.module_template_location)
            class_ = getattr(modules, self.module)
            instance = class_(**self.kwargs)
            return instance
        except Exception as ex:
            raise InvalidModuleException(
                message=f"[{self.__class__.__name__}] {self.module} not found settings config IMPORT_MODULE_TEMPLATE or error validate NotImplementedError in {self.module}",
                verbose=True)

    def load_module(self):
        return self.get_module_define()
