from app.financial.variable.common import DONE_STATUS, ERROR_STATUS, OPEN_STATUS, PROCESS_STATUS

EVERY_5_MINUTE = 'every_5_minute'
EVERY_15_MINUTE = 'every_15_minute'
EVERY_1_HOUR = 'every_1_hour'
EVERY_2_HOUR = 'every_2_hour'
EVERY_6_HOUR = 'every_6_hour'
EVERY_12_HOUR = 'every_12_hour'
EVERY_24_HOUR = 'every_24_hour'

REFRESH_RATE_CONFIG = (
    (EVERY_5_MINUTE, 'Every 5 minutes'),
    (EVERY_15_MINUTE, 'Every 15 minutes'),
    (EVERY_1_HOUR, 'Every 1 hour'),
    (EVERY_24_HOUR, 'Every day')
)

THROTTLING_PERIOD = (
    (EVERY_1_HOUR, '1 Hour'),
    (EVERY_2_HOUR, '2 Hour'),
    (EVERY_6_HOUR, '6 Hour'),
    (EVERY_12_HOUR, '12 Hour'),
    (EVERY_24_HOUR, '24 Hour')
)

CONVERT_EVERY_CONFIG_TO_MINUTES = {
    EVERY_5_MINUTE: 5,
    EVERY_15_MINUTE: 15,
    EVERY_1_HOUR: 60,
    EVERY_2_HOUR: 2 * 60,
    EVERY_6_HOUR: 6 * 60,
    EVERY_12_HOUR: 12 * 60,
    EVERY_24_HOUR: 24 * 60
}

# via
EMAIL_VARIABLE = 'email'
SMS_VARIABLE = 'sms'
WEB_PUSH_VARIABLE = 'web_push'

ALERT_DELIVERY_VIA_ENUMS = (
    (EMAIL_VARIABLE, 'Email'),
    (SMS_VARIABLE, 'SMS'),
    (WEB_PUSH_VARIABLE, 'Web Push Notification')
)

ALERT_DELIVERY_STATUS_ENUMS = (
    (OPEN_STATUS, OPEN_STATUS),
    (PROCESS_STATUS, PROCESS_STATUS),
    (ERROR_STATUS, ERROR_STATUS),
    (DONE_STATUS, DONE_STATUS)
)
