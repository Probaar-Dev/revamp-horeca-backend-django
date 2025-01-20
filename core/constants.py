from django.utils.translation import gettext_lazy as _

ACTIONS = {
    'add': {
        'title': _("add"),
        'level': 'primary',
        'icon': 'plus',
        'permission_prefix': 'add',
    },
    'change': {
        'title': _("change"),
        'level': 'primary',
        'icon': 'pencil',
        'permission_prefix': 'change',
    },
    'delete': {
        'title': _("delete"),
        'level': 'danger',
        'icon': 'trash',
        'permission_prefix': 'delete',
    },
    'run': {
        'title': _("run"),
        'level': 'danger',
        'icon': 'clock',
        'permission_prefix': 'change',
    },
    'verify': {
        'title': _("verify"),
        'level': 'primary',
        'icon': 'tick',
        'permission_prefix': 'change',
    },
    'view': {
        'title': _("view"),
        'level': 'info',
        'icon': 'eye-open',
        'permission_prefix': 'view',
    },
    'cancel': {
        'title': _("cancel"),
        'level': 'danger',
        'icon': 'ban',
        'permission_prefix': 'change',
    },
}

DIRECTION_INBOUND = 'inbound'
DIRECTION_OUTBOUND = 'outbound'

GENDER_MALE = 'male'
GENDER_FEMALE = 'female'
GENDER_OTHER = 'other'

SHOW_ONBOARDING_MODAL_TRUE = 'true'
SHOW_ONBOARDING_MODAL_FALSE = 'false'

LEVEL_ERROR = 'error'
LEVEL_SUCCESS = 'success'
LEVEL_WARNING = 'warning'

PLACE_BAR = 'bar'
PLACE_DISCO = 'disco'
PLACE_RESTAURANT = 'restaurant'
PLACE_STORE = 'store'
PLACE_GENERAL = 'general'
PLACE_WAREHOUSE = 'warehouse'

BLOCK_REASON_GENERAL = 'blocked'
BLOCK_REASON_PAYMENT = 'lack_of_payment'
BLOCK_REASON_VERIFICATION_PENDING = 'verification_pending'

UNBLOCK_REASON_PAYMENT = 'payment'
UNBLOCK_REASON_TEMPORAL_UNBLOCK = 'temporal_unblock'

DOCUMENT_DNI_LENGTH = 8
DOCUMENT_RUC_LENGTH = 11

EXTRA_DAYS_FOR_DUE_INVOICES = 3

PERU_IGV_TAX_RATE = 0.18

CRONJOB_SYNC_ODOO_FLAG = 'sync_odoo_blocked'
CRONJOB_REBUILD_INDEX_FLAG = 'sync_rebuild_index'

PAYMENT_METHOD_CASH_DEPOSIT = 'CASH_DEPOSIT'
PAYMENT_METHOD_CREDIT = 'CREDIT'

ODOO_PAYMENT_TERM_CASH = 'Immediate Payment'

# Inventory move states
STATE_DRAFT = 'draft'
STATE_DONE = 'done'

WEEKDAY_MONDAY = 'monday'
WEEKDAY_TUESDAY = 'tuesday'
WEEKDAY_WEDNESDAY = 'wednesday'
WEEKDAY_THURSDAY = 'thursday'
WEEKDAY_FRIDAY = 'friday'
WEEKDAY_SATURDAY = 'saturday'
WEEKDAY_SUNDAY = 'sunday'

WEEKDAYS = (
    WEEKDAY_MONDAY, WEEKDAY_TUESDAY, WEEKDAY_WEDNESDAY,
    WEEKDAY_THURSDAY, WEEKDAY_FRIDAY, WEEKDAY_SATURDAY, WEEKDAY_SUNDAY,
)
