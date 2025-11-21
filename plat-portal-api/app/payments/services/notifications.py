import json
from datetime import datetime, timezone
from typing import List, Union

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

from app.core.logger import logger
from app.payments.config import ACTIVITY_GRADE_CHANGE, APP_TRANSIT
from app.payments.models import FundPackage, Subscription, SubscriptionActivity
from app.payments.services.stripe_invoice import StripeInvoiceService
from app.tenancies.models import Organization, OrganizationUser, Setting, User


class PaymentEmailNotification:
    def __init__(
            self,
            subscription: Union[Subscription, None],
            external_subscription_id: str,
            transaction_data,
            *args,
            **kwargs,
    ):
        if not subscription:
            subscription = Subscription.objects.get(
                external_subscription_id=external_subscription_id
            )
        self.subscription = subscription
        self.recipient_list = [subscription.user.email]
        self.transaction_data = transaction_data
        self.team_name = settings.TEAM_NAME
        self.extra_infomation = kwargs

    def __send(self, subject_name, html_rendered):
        logger.info(f"[{self.__class__.__name__}][send]")
        msg = EmailMessage(
            subject=subject_name,
            body=html_rendered,
            from_email=settings.DJANGO_DEFAULT_FROM_EMAIL,
            to=self.recipient_list,
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

    def __send_email_alternatives(self, subject_name, html_rendered):
        logger.info(f"[{self.__class__.__name__}][__send_email_alternatives]")
        msg = EmailMultiAlternatives(
            subject=subject_name,
            body=html_rendered,
            from_email=settings.DJANGO_DEFAULT_FROM_EMAIL,
            to=self.recipient_list,
        )
        msg.attach_alternative(html_rendered, "text/html")
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

    @classmethod
    def __convert_number(cls, number):
        if number in [-1, None]:
            return "unlimited"
        return f"{number:,}"

    def mail_has_subscribed(self):
        subject_name = f"{self.subscription.organization.name} - Subscription invoice - {self.subscription.plan.name}"
        criteria_list = self.subscription.plan.criteria or []

        invoice_pdf = self.transaction_data.get("invoice_pdf")
        hosted_invoice_url = self.transaction_data.get("hosted_invoice_url")

        criteria_list.extend(
            [
                f"Max workspaces: {self.__convert_number(self.subscription.plan.max_workspaces)}",
                f"Max internal users: {self.__convert_number(self.subscription.plan.max_internal_users)}",
                f"Max external users: {self.__convert_number(self.subscription.plan.max_external_users)}",
            ]
        )
        data = {
            "receiver_name": self.subscription.user.name
                             or self.subscription.user.username,
            "plan_name": self.subscription.plan.name,
            "criteria_list": criteria_list,
            "plan_description": self.subscription.plan.description,
            "invoice_pdf": invoice_pdf,
            "hosted_invoice_url": hosted_invoice_url,
            "team_name": self.team_name,
        }

        if self.subscription.application == APP_TRANSIT:
            # get videos tutorial
            videos_tutorial = self.__get_video_tutorial()
            if len(videos_tutorial):
                data.update({"videos_tutorial": videos_tutorial})

        html_rendered = render_to_string("payment_notification/subscribe.html", data)
        self.__send_email_alternatives(subject_name, html_rendered)

    def mail_trial_will_end(self):
        subject_name = f"{self.subscription.organization.name} - Trial will end - {self.subscription.plan.name}"
        trial_end = datetime.fromtimestamp(
            self.transaction_data.get("trial_end"), tz=timezone.utc
        )
        time_delta = trial_end - datetime.now(tz=timezone.utc)
        remaining_hours = int(time_delta.seconds / (60 * 60))
        if time_delta.days:
            remaining_hours += time_delta.days * 24
        data = {
            "receiver_name": self.subscription.user.name
                             or self.subscription.user.username,
            "plan_name": self.subscription.plan.name,
            "remaining_hours": remaining_hours,
            "trial_end": trial_end,
            "trial_end_date": trial_end.date(),
            "trial_end_time": trial_end.time(),
            "team_name": self.team_name,
        }
        html_rendered = render_to_string(
            "payment_notification/trial_will_end.html", data
        )
        self.__send(subject_name, html_rendered)

    def mail_unsubscribe(self):
        subject_name = f"{self.subscription.organization.name} - Unsubscribe the plan - {self.subscription.plan.name}"
        data = {
            "receiver_name": self.subscription.user.name
                             or self.subscription.user.username,
            "plan_name": self.subscription.plan.name,
            "team_name": self.team_name,
        }
        html_rendered = render_to_string("payment_notification/unsubscribe.html", data)
        self.__send(subject_name, html_rendered)

    def mail_grade_changes(self, user: User, *args, **kwargs):
        plan_name = self.subscription.plan.name
        subject_name = f"{self.subscription.organization.name} - Subscription plan changed to {plan_name}"

        self.recipient_list = self.__get_list_emails(user)

        data = self.__prepare_invoice_data(user)
        data.update(
            {
                "current_plan": self.subscription.plan.name,
                "subscription_proration_date": datetime.fromtimestamp(
                    self.extra_infomation.get("subscription_proration_date"),
                    tz=timezone.utc,
                ),
            }
        )
        data.update(kwargs)

        html_rendered = render_to_string(
            "payment_notification/grade_changes.html", data
        )
        self.__send(subject_name, html_rendered)

    def mail_incoming_invoice(self, user):
        subject_name = f"{settings.APP_NAME} - {self.subscription.organization.name} - Upcoming Billing Statement"

        self.recipient_list = self.__get_list_emails(user)

        data = self.__prepare_invoice_data(user)

        html_rendered = render_to_string(
            "payment_notification/incoming_invoice.html", data
        )
        self.__send(subject_name, html_rendered)

    def __get_list_emails(self, user: User):
        list_email = (
            SubscriptionActivity.objects.filter(
                subscription=self.subscription, action=ACTIVITY_GRADE_CHANGE
            )
            .values_list("user__email", flat=True)
            .distinct()
        )
        list_email = list(list_email)
        list_email.extend([user.email, self.subscription.user.email])
        return list(set(list_email))

    def __prepare_invoice_data(self, user: User) -> dict:
        default_data = {
            "receiver_name": user.name or user.username,
            "plan_name": self.subscription.plan.name,
            "team_name": self.team_name,
        }
        extracted_data = StripeInvoiceService(
            self.extra_infomation.get("incoming_invoice")
        ).output()
        data = {
            **self.extra_infomation,
            **extracted_data,
            **default_data,
        }
        subtotal, discount_total, total, amount, applied_balance = (
            data.get("subtotal", 0) / 100,
            data.get("discount_total", 0) / 100,
            data.get("total", 0) / 100,
            data.get("amount", 0) / 100,
            data.get("applied_balance", 0) / 100,
        )

        period_start = datetime.fromtimestamp(
            data.get("period_start"), tz=timezone.utc
        ).date()
        period_end = datetime.fromtimestamp(
            data.get("period_end"), tz=timezone.utc
        ).date()
        data.update(
            {
                "period_start": period_start,
                "period_end": period_end,
                "subtotal": f"${subtotal}" if subtotal >= 0 else f"- ${subtotal * -1}",
                "discount_total": f"${discount_total}"
                if discount_total >= 0
                else f"- ${discount_total * -1}",
                "total": f"${total}" if total >= 0 else f"- ${total * -1}",
                "amount": f"${amount}" if amount >= 0 else f"- ${amount * -1}",
                "applied_balance": f"${applied_balance}"
                if applied_balance >= 0
                else f"- ${applied_balance * -1}",
            }
        )
        return data

    def mail_adding_packages(
            self, user: User, fund_package: FundPackage, receipt_url: str
    ):
        subject_name = f"{self.subscription.organization.name} - Add credit invoice - {fund_package.name}"

        list_email = [self.subscription.user.email, user.email]

        self.recipient_list = list(set(list_email))

        data = {
            "receiver_name": user.name or user.username,
            "team_name": self.team_name,
        }
        data.update(
            {
                "credit": self.__convert_number(fund_package.balance),
                "package_name": fund_package.name,
                "receipt_url": receipt_url,
            }
        )

        html_rendered = render_to_string("payment_notification/adding_fund.html", data)
        self.__send(subject_name, html_rendered)

    def mail_payment_fail(self, user: User):
        subject_name = f"{settings.APP_NAME} - {self.subscription.organization.name} - Payment Fail"

        self.recipient_list = [user.email]
        data = {
            "receiver_name": user.name or user.username,
            "plan_name": self.subscription.plan.name,
            "team_name": self.team_name,
        }
        html_rendered = render_to_string("payment_notification/payment_fail.html", data)
        self.__send(subject_name, html_rendered)

    def mail_payment_fail_admin(self):
        subject_name = f"{settings.APP_NAME} - {self.subscription.organization.name} - Payment Fail"
        setting_admin = Setting.objects.filter(name="default").first()
        self.recipient_list = list(getattr(setting_admin, "emails", []))
        data = {
            "receiver_name": "system admin",
            "plan_name": self.subscription.plan.name,
            "team_name": self.team_name,
            "organization_name": self.subscription.organization.name,
            "expired_in": self.subscription.expired_in,
            "owner_name": self.subscription.user.name
                          or self.subscription.user.username,
            "owner_email": self.subscription.user.email,
            "application": settings.APP_NAME,
        }
        html_rendered = render_to_string(
            "payment_notification/payment_fail_admin.html", data
        )
        self.__send(subject_name, html_rendered)

    def __get_app_config(self, path_file_config: str) -> dict:
        try:
            with open(path_file_config, "r") as _file:
                return json.load(_file)
        except Exception as err:
            logger.error(f"[{self.__class__.__name__}][__get_app_config] {err}")
            return {}

    def __get_video_tutorial(self) -> List:
        """
        get video tutorial for transit app
        """

        app_json_config = self.__get_app_config(
            path_file_config="./config/transit_app/videos_tutorial.json"
        )
        videos_tutorial = app_json_config.get("videos_tutorial", [])
        if len(videos_tutorial) == 1:
            videos_tutorial = [
                {
                    "label": "Getting Started with 2D Transit",
                    "link": videos_tutorial[0],
                }
            ]
        else:
            videos_tutorial = [
                {
                    "label": f"Getting Started with 2D Transit - Part {_idx + 1}",
                    "link": vid,
                }
                for _idx, vid in enumerate(videos_tutorial)
            ]
        return videos_tutorial


def notify_low_organization_balance(
        organization_id: str, subject_name: str, message_text: str
):
    org = Organization.objects.get(id=organization_id)
    org_users = OrganizationUser.objects.filter(
        organization_id=organization_id, role__key__in=["OWNER", "MANAGER", "ADMIN"]
    ).select_related("user")

    for org_user in org_users:
        receiver_name = org_user.user.name or org_user.user.username
        recipient_list = [org_user.user.email]
        data = {
            "org_name": org.name,
            "team_name": settings.TEAM_NAME,
            "receiver_name": receiver_name,
            "message_text": message_text,
        }
        html_rendered = render_to_string("payment_notification/low_balance.html", data)

        msg = EmailMessage(
            subject=subject_name,
            body=html_rendered,
            from_email=settings.DJANGO_DEFAULT_FROM_EMAIL,
            to=recipient_list,
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
