CHANGE_TO = 'change_to'
ADD = 'add'
SUBTRACT = 'subtract'
MULTIPLY_BY = 'multiply_by'
DIVIDE_BY = 'divide_by'
PERCENT_INCREASE = 'percent_increase'
PERCENT_DECREASE = 'percent_decrease'
UNDO_PERCENT_INCREASE = 'undo_percent_increase'
UNDO_PERCENT_DECREASE = 'undo_percent_decrease'
APPEND = 'append'
PREPEND = 'prepend'

BULK_EDIT_COMMON_ACTION_CHOICE = (
    (CHANGE_TO, 'Change Value'),
)
BULK_EDIT_COMMON_LIST = list(item[0] for item in BULK_EDIT_COMMON_ACTION_CHOICE)

BULK_EDIT_NUMERIC_ACTION_CHOICE = (
    (ADD, 'Add Value'),
    (SUBTRACT, 'Subtract Value'),
    (MULTIPLY_BY, 'Multiply By Value'),
    (DIVIDE_BY, 'Divide By Value'),
    (PERCENT_INCREASE, 'Increase Value By Percent'),
    (PERCENT_DECREASE, 'Decrease Value By Percent'),
    (UNDO_PERCENT_INCREASE, 'Undo Increase Value By Percent'),
    (UNDO_PERCENT_DECREASE, 'Undo Decrease Value By Percent')
)
BULK_EDIT_NUMERIC_ACTION_LIST = list(item[0] for item in BULK_EDIT_NUMERIC_ACTION_CHOICE)

BULK_EDIT_TEXT_ACTION_CHOICE = (
    (APPEND, 'Append'),
    (PREPEND, 'Prepend')
)
BULK_EDIT_TEXT_ACTION_LIST = list(item[0] for item in BULK_EDIT_TEXT_ACTION_CHOICE)

BULK_EDIT_ACTION_CHOICE = BULK_EDIT_COMMON_ACTION_CHOICE + BULK_EDIT_NUMERIC_ACTION_CHOICE + \
                          BULK_EDIT_TEXT_ACTION_CHOICE
BULK_EDIT_ACTION_LIST = list(item[0] for item in BULK_EDIT_ACTION_CHOICE)
