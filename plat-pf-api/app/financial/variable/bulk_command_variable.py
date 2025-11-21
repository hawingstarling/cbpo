EDIT = 'edit'
DELETE = 'delete'
SYNC = 'sync'

BULK_COMMAND_CHOICE = (
    (EDIT, 'Edit'),
    (DELETE, 'Delete'),
    (SYNC, 'Sync'),
)
BULK_COMMAND_LIST = list(item[0] for item in BULK_COMMAND_CHOICE)
