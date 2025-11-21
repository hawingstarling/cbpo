from django.conf import settings

# Choices for Module - enum type
MODULE_ENUM = (
    ("MAP", "MAP Watcher"),
    ("ROG", "Rogue Watcher"),
    ("DS", "Data Sources"),
    ("RA", "Reporting Application"),
    ("MT", "Matrix"),
    ("DC", "Data Central"),
    ("PF", "Precise Financial"),
    ("TR", "2D Transit"),
    ("SKUF", "SKUFlex"),
)

# Status member in table user - client
IS_MEMBER = "MEMBER"
IS_PENDING = "PENDING"
MEMBER_STATUS = ((IS_MEMBER, "Member"), (IS_PENDING, "Pending"))

# Type of Notification
TYPE_NOTIFICATION = (("INVITATION", "Invitation"), ("WARNING", "Warning"))

# Action of Activity
ACTION_ACTIVITY_OBJ = dict()

ACTION_ACTIVITY = (
    ("SIGN_IN", "Sign In"),
    ("DOWNLOAD_MAP_REPORT", "Download MAP Report"),
    ("DOWNLOAD_ROG_REPORT", "Download ROG Report"),
    ("ACCESS_WORKSPACE", "Access Workspace"),
    ("ADD_MEMBER", "Add Member" ),
    ("UPDATE_MEMBER", "Update Member" ),
    ("DELETE_MEMBER", "Delete Member" )
)

for key, value in ACTION_ACTIVITY:
    ACTION_ACTIVITY_OBJ.update({key: value})

NOTIFICATION_STATUS = (("OPEN", "Open"), ("DONE", "Done"))

# Role for Role Model
role_name = ["Owner", "Admin", "Staff", "Client"]

# The time for token be expired
TIME_FOR_TOKEN_EXPIRED = 30  # minutes

# Maximum times for requiring code per day
TIMES_PER_DAY = 3

# Number of days for token being available for invitation
DAYS_EXPIRED = 7

# name of folder image for uploading images
TYPE = ["user_photos", "client_logos"]
TYPE_IMAGE = ["png", "jpg", "jpeg"]

WHITE_LIST_DOMAIN = [
    "localhost",
    settings.DOMAIN_CP,
    settings.DOMAIN_OE,
    settings.DOMAIN_2D,
]

ORGANIZATION_DEFAULT = "Channel Precision"

# Account manager domain
REGEX_INTERNAL_USER_DOMAINS = r"^[a-zA-Z0-9_.+-]+@(?:(?:[a-zA-Z0-9-]+\.)?[a-zA-Z]+\.)?(hdwebsoft|outdoorequipped|channelprecision)\.com$"
