import hashlib

import mailchimp_marketing
from django.conf import settings
from mailchimp_marketing.api_client import ApiClientError

from app.core.logger import logger
from app.tenancies.models import User

MAILCHIMP_CONFIG = settings.MAILCHIMP_CONFIG

_mailchimp_marketing_client = mailchimp_marketing.Client()
_mailchimp_marketing_client.set_config(
    {
        "api_key": MAILCHIMP_CONFIG.get("MAILCHIMP_API_KEY"),
        "server": MAILCHIMP_CONFIG.get("MAILCHIMP_PREFIX_SERVER"),
    }
)

MAILCHIMP_TAG_KEY = "tags"
MAILCHIMP_TAG_PAID_KEY = "PAID"
MAILCHIMP_PLAN_KEY = "PLAN"

# valid tag keys configured on mailchimp
MAILCHIMP_AVAILABLE_TAGS = ["STANDARD", "PROFESSIONAL", "BUSINESS", "CUSTOM", MAILCHIMP_TAG_PAID_KEY]


class _MailchimpService:
    def __init__(self):
        self._client = _mailchimp_marketing_client

    def update_member(self, user: User, extra_kwargs: dict):
        email_hashed = hashlib.md5(user.email.encode("utf-8").lower()).hexdigest()

        member_info = {
            "email_address": user.email,
            "status": "subscribed",
            "status_if_new": "subscribed",
        }
        # update info and merge vars
        merge_fields = {}

        if user.first_name:
            merge_fields.update({"FNAME": user.first_name})
        if user.last_name:
            merge_fields.update({"LNAME": user.last_name})
        if merge_fields != {}:
            member_info.update({"merge_fields": merge_fields})

        _plan = extra_kwargs.get(MAILCHIMP_PLAN_KEY, None)
        if _plan:
            merge_fields.update({MAILCHIMP_PLAN_KEY: _plan})

        try:
            _ = self._client.lists.set_list_member(MAILCHIMP_CONFIG.get("MAILCHIMP_LIST_ID"), email_hashed, member_info)

        except ApiClientError as err:
            logger.error("{}: {}".format(self.__class__.__name__, err.text))

        # set tag for the contact
        tags = extra_kwargs.get(MAILCHIMP_TAG_KEY, [])
        if len(tags):
            try:
                parsed_tags = [{"name": _ele, "status": "active"} for _ele in tags if _ele in MAILCHIMP_AVAILABLE_TAGS]
                _ = self._client.lists.update_list_member_tags(
                    MAILCHIMP_CONFIG.get("MAILCHIMP_LIST_ID"), email_hashed, {"tags": parsed_tags}
                )
            except ApiClientError as err:
                logger.error("{}: {}".format(self.__class__.__name__, err.text))

    def subscribe_new_users(self, user: User):
        """

        @param user:
        """
        member_info = {
            "email_address": user.email,
            "status": "subscribed",
            "status_if_new": "subscribed",
        }
        merge_fields = {}

        if user.first_name:
            merge_fields.update({"FNAME": user.first_name})
        if user.last_name:
            merge_fields.update({"LNAME": user.last_name})
        if merge_fields != {}:
            member_info.update({"merge_fields": merge_fields})

        try:
            email_hashed = hashlib.md5(user.email.encode("utf-8").lower()).hexdigest()
            _ = self._client.lists.set_list_member(MAILCHIMP_CONFIG.get("MAILCHIMP_LIST_ID"), email_hashed, member_info)
        except ApiClientError as err:
            logger.error("{} {}".format(self.__class__.__name__, err.text))


mailchimp_handler = _MailchimpService()


def add_member_mailchimp(user: User):
    mailchimp_handler.subscribe_new_users(user=user)
