import logging
from celery import current_app
from django.db import DEFAULT_DB_ALIAS
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import override

from app.core.services.workspace_management import WorkspaceManagement
from app.financial.models import DivisionClientUserWidget, DivisionManage, WidgetConfig, ClientPortal, \
    ClientDashboardWidget, \
    ClientSettings
from app.financial.services.brand_settings.brand_setting_manage import BrandSettingManage
from app.financial.services.financial_notification import FinancialNotification

logger = logging.getLogger(__name__)


@current_app.task(bind=True)
def init_client_setting_default(self, client_id):
    logger.info(f"[Tasks][{self.request.id}][{client_id}] Init client setting default")
    ClientSettings.objects.tenant_db_for(client_id).get_or_create(client_id=client_id)


@current_app.task(bind=True)
def handler_notice_new_missing_brand(self, client_id):
    logger.info(f"[Tasks][{self.request.id}][{client_id}] Notices new missing brands via system contacts")
    FinancialNotification(client_id).notify_missing_brands()


@current_app.task(bind=True)
def handler_notice_no_brand_settings(self, client_id):
    logger.info(f"[Tasks][{self.request.id}][{client_id}] Notices no brand settings via system contacts")
    FinancialNotification(client_id).notify_no_brand_settings()


#
@current_app.task(bind=True)
def handler_checking_status_deactivate_of_workspace(self, client_id):
    #
    logger.info(f"[Tasks][{self.request.id}][{client_id}][handler_checking_status_deactivate_of_workspace] "
                f"Begin checking status of workspace from portal ...")
    WorkspaceManagement(client_id=client_id).sync_status_of_client()


@current_app.task(bind=True)
def handler_delete_brand_setting(self, client_id, brand_id, **kwargs):
    logger.info(
        f"[Tasks][{self.request.id}][{client_id}][handler_delete_brand_setting] Begin handler delete brand setting ....")
    brand_manage = BrandSettingManage(client_id=client_id, brand_id=brand_id, **kwargs)
    brand_manage.delete()


@current_app.task(bind=True)
def handler_init_client_dashboard_widget(self, client_ids: [str], **kwargs):
    logger.info(f"[Tasks][{self.request.id}][{client_ids}][handler_init_client_dashboard_widget] "
                f"Begin handler ....")
    clients = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).all()
    if client_ids:
        clients = clients.filter(pk__in=client_ids)

    override_position = kwargs.get('override_position', False)
    override_proportion = kwargs.get('override_proportion', False)

    for client in clients:
        clients_widgets_inserts = []
        clients_widgets_updates = []
        client_id = client.pk
        widgets = WidgetConfig.objects.tenant_db_for(client_id).all()
        widget_ids = list(widgets.values_list('pk', flat=True))
        for widget in widgets:
            try:
                obj = ClientDashboardWidget.objects.tenant_db_for(client_id).get(client_id=client_id, widget=widget)
                if not override_position and not override_proportion:
                    continue
                if override_position:
                    obj.position = widget.position
                    obj.position_default = widget.position
                if override_proportion:
                    obj.proportion = widget.proportion
                obj.modified = timezone.now()
                clients_widgets_updates.append(obj)  # update
            except Exception as ex:
                logger.error(f"[Tasks][{self.request.id}][{client_id}][handler_init_client_dashboard_widget] {ex}")
                obj = ClientDashboardWidget(
                    client_id=client_id,
                    widget=widget,
                    position=widget.position,
                    proportion=widget.proportion,
                    position_default=widget.position
                )
                clients_widgets_inserts.append(obj)

        if clients_widgets_inserts:
            logger.info(
                f"[Tasks][{self.request.id}][{client_ids}][handler_init_client_dashboard_widget] "
                f"{len(clients_widgets_inserts)} inserts")
            ClientDashboardWidget.objects.tenant_db_for(client_id).bulk_create(clients_widgets_inserts,
                                                                               ignore_conflicts=True)

        if clients_widgets_updates:
            logger.info(
                f"[Tasks][{self.request.id}][{client_ids}][handler_init_client_dashboard_widget] "
                f"{len(clients_widgets_inserts)} updates")
            ClientDashboardWidget.objects.tenant_db_for(client_id).bulk_update(clients_widgets_updates,
                                                                               fields=['position', 'position_default',
                                                                                       'proportion', 'modified'], )

        ClientDashboardWidget.objects.tenant_db_for(client_id).filter(~Q(widget_id__in=widget_ids)).delete()


@current_app.task(bind=True)
def handler_init_sync_divisions_widget_clients(self, client_ids: [str], **kwargs):
    logger.info(f"[Tasks][{self.request.id}][{client_ids}][handler_init_sync_divisions_widget_clients] "
                f"Begin handler ....")
    clients = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).all()
    if client_ids:
        clients = clients.filter(pk__in=client_ids)

    override_settings = kwargs.get('override_settings', False)
    override_positions = kwargs.get('override_positions', False)

    queryset = DivisionManage.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(is_active=True)

    division_client_inserts = []
    division_client_updates = []
    for client in clients:
        client_id = client.pk
        for division in queryset.order_by("-created"):
            try:
                obj = DivisionClientUserWidget.objects.tenant_db_for(DEFAULT_DB_ALIAS).get(
                    client_id=client_id,
                    category=division.category,
                    key=division.key
                )
                if not override_settings and not override_positions:
                    continue
                if override_settings:
                    obj.settings = division.settings
                if override_positions:
                    obj.position = division.position
                    obj.position_default = division.position
                obj.modified = timezone.now()
                division_client_updates.append(obj)
            except DivisionClientUserWidget.DoesNotExist:
                obj = DivisionClientUserWidget(
                    client_id=client_id,
                    category=division.category,
                    key=division.key,
                    name=division.name,
                    settings=division.settings,
                    position=division.position,
                    position_default=division.position
                )
                division_client_inserts.append(obj)
            except Exception as ex:
                logger.error(
                    f"[Tasks][{self.request.id}][{client_id}][handler_init_sync_divisions_widget_clients] {ex}")
    if division_client_inserts:
        logger.info(
            f"[Tasks][{self.request.id}][{client_ids}][handler_init_sync_divisions_widget_clients] "
            f"{len(division_client_inserts)} inserts")
        DivisionClientUserWidget.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_create(division_client_inserts,
                                                                                     ignore_conflicts=True)

    if division_client_updates:
        logger.info(
            f"[Tasks][{self.request.id}][{client_ids}][handler_init_sync_divisions_widget_clients] "
            f"{len(division_client_updates)} updates")
        DivisionClientUserWidget.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
            .bulk_update(division_client_updates, fields=["settings", "position", "position_default", "modified"])
