from django.utils.translation import gettext_lazy as _


def default_error_message(field: str = None, max_length=None):
    error_messages = {
        'required': _('{} is required'.format(field)),
        'null': _('{} cannot be null'.format(field)),
        'invalid': _('{} is invalid'.format(field)),
        'blank': _('{} field may not be blank'.format(field)),
        'max_length': _('{} max length is {}'.format(field, 256)),
        'max_digits': _('{} max digits is 6'.format(field))
    }
    if max_length:
        error_messages.update({'max_length': _('{} max length is {}'.format(field, max_length))})
    return error_messages
