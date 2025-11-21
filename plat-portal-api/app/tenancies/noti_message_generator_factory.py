from abc import ABC
from app.tenancies.config_static_variable import TYPE_NOTIFICATION
from django.contrib.contenttypes.models import ContentType


class IMessageGenerator(ABC):

    def __init__(self, notification_instance, *args, **kwargs):
        self.notification_instance = notification_instance

    @classmethod
    def message_generator(cls, *args, **kwargs):
        """
        the message generator interface
        """


class InvitationalNotification(IMessageGenerator):

    def message_generator(self, *args, **kwargs):
        work_space = self.notification_instance.object.name
        author = self.notification_instance.author.name
        content = ContentType.objects.get_for_model(self.notification_instance.object)
        args = {
            'organization': 'Organization',
            'client': 'Workspace'
        }
        name_invite = args.get(content.model, None)
        message = "You are invited to %s %s by %s" % (name_invite, work_space, author)
        return message


class WarningNotification(IMessageGenerator):

    def message_generator(self, *args, **kwargs):
        message = "WARNING"
        return message


class NotificationMessageFactory:
    """
    Notification Message Generator Factory Based on Notification Instance
    """

    @staticmethod
    def get_message_instance(type_notification, notification_instance):
        if type_notification == TYPE_NOTIFICATION[0][0]:
            return InvitationalNotification(notification_instance)
        if type_notification == TYPE_NOTIFICATION[1][0]:
            return WarningNotification(notification_instance)
