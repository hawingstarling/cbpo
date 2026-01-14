from django.apps import AppConfig


class PermissionConfig(AppConfig):
    name = 'app.permission'
    
    def ready(self):
        """Initialize permission bitset registry when app is ready."""
        from app.permission.bitset_permissions import initialize_permission_registry
        initialize_permission_registry()