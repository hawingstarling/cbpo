from itertools import groupby
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.utils import DEFAULT_DB_ALIAS
from django.template.loader import render_to_string
from app.core.logger import logger
from app.financial.models import BrandMissing, FinancialSettings
from app.financial.services.brand_settings.alert_no_brand_settings import alert_no_brand_settings


class FinancialNotification:

    def __init__(self, client_id: str, **kwargs):
        self.client_id = client_id
        self.kwargs = kwargs

    def notify_missing_brands(self):
        new_missing_brands = list(BrandMissing.objects.tenant_db_for(self.client_id).filter(is_noticed=False))
        if not len(new_missing_brands):
            return
        try:
            financial_settings = FinancialSettings.objects.tenant_db_for(DEFAULT_DB_ALIAS).first()
            list_emails = financial_settings.system_contacts
        except Exception as error:
            logger.error(f'{error}')
            logger.warn(f'[{self.__class__.__name__}] client PF Development has no system_contacts')
            list_emails = []

        if not len(list_emails):
            return

        EmailServices().send_new_missing_brands('PF Development', list_emails)
        new_missing_brands_ids = [item.id for item in new_missing_brands]
        BrandMissing.objects.tenant_db_for(self.client_id).filter(id__in=new_missing_brands_ids).update(
            is_noticed=True)

    def notify_no_brand_settings(self):
        try:
            financial_settings = FinancialSettings.objects.tenant_db_for(DEFAULT_DB_ALIAS).first()
            if financial_settings.no_brand_setting_notification is False:
                return
            list_emails = financial_settings.no_brand_setting_notification_emails
        except Exception as error:
            logger.error(f'{error}')
            logger.warn(
                f'[{self.__class__.__name__}] client PF Development has no no_brand_setting_notification_emails')
            list_emails = []

        if not len(list_emails):
            return

        no_brand_settings_data = alert_no_brand_settings(self.client_id)
        no_brand_settings_data.sort(key=lambda ele: ele.client_name)

        client_data_for_render = []

        for group_key, group_value in groupby(no_brand_settings_data, lambda ele: (ele.client_name, ele.client_id)):
            brand_names = [item.brand_name for item in group_value]
            brand_names.sort()
            client_data_for_render.append({
                'client_name': group_key[0],
                'client_id': str(group_key[1]),
                'brand_names': brand_names
            })

        if not len(client_data_for_render):
            return

        EmailServices().send_recent_sale_has_no_brand_settings('PF Development', client_data_for_render, list_emails)


class EmailServices:

    @staticmethod
    def send_email(subject, msg_html, recipient_list: [str], sender_name: str = "Admin"):
        email_from = f"{sender_name} {settings.DJANGO_DEFAULT_FROM_EMAIL}"
        msg = EmailMessage(subject=subject, body=msg_html, from_email=email_from, to=recipient_list)
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

    def send_new_missing_brands(self, team_name: str, recipient_list: [str]):
        subject = 'PF new missing brand (%s)' % settings.ENVIRONMENT
        admin_missing_brand_page = f'{settings.BASE_URL}/admin/financial/brandmissing/?custom_mapped_brand=not_mapped'
        data = {'receiver_name': "admin",
                'team_name': team_name,
                'admin_missing_brand_page': admin_missing_brand_page,
                }
        msg_html = render_to_string('system/notice_missing_brands.html', data)
        self.send_email(subject, msg_html, recipient_list)

    def send_recent_sale_has_no_brand_settings(self, team_name, client_data, recipient_list: [str]):
        subject = 'PF no brand settings (%s)' % settings.ENVIRONMENT
        data = {'receiver_name': "there",
                'team_name': team_name,
                'client_data': client_data}
        msg_html = render_to_string('system/notice_no_brand_settings.html', data)
        self.send_email(subject, msg_html, recipient_list)

    def send_bulk_processing(self, team_name, receiver_name, description, items, recipient_list: [str]):
        subject = 'PF bulk processing (%s)' % settings.ENVIRONMENT
        data = {'receiver_name': receiver_name,
                'team_name': team_name,
                'description': description,
                'items': items}
        msg_html = render_to_string('client/notice_bulk_processing.html', data)
        self.send_email(subject, msg_html, recipient_list)

    def send_stats_report_daily(self, team_name: str, receiver_name: str, items: dict, recipient_list: [str]):
        subject = 'PF stats (%s)' % settings.ENVIRONMENT
        data = {
            'subject': subject,
            'receiver_name': receiver_name,
            'team_name': team_name,
            'items': items
        }
        msg_html = render_to_string('system/stats.html', data)
        self.send_email(subject, msg_html, recipient_list)

    def send_sale_alert(self, team_name: str, receiver_name: str, view_name: str, ref_link: str, items: [dict],
                        recipient_list: [str]):
        sender_name = "Precise Financial Alerts"
        subject = f'PF Alert for `{view_name}` - New Sale(s) found ({settings.ENVIRONMENT})'
        data = {
            'subject': subject,
            'receiver_name': receiver_name,
            'team_name': team_name,
            'ref_link': ref_link,
            'view_name': view_name,
            'items': items
        }
        msg_html = render_to_string('alert/notice_sale_custom_view.html', data)
        self.send_email(subject, msg_html, recipient_list, sender_name)
