from django.db import models
from django.utils.translation import gettext_lazy as _

NO_CONFLICT_STATUS = "No conflict"
CONFLICT_STATUS = "In conflict"


class ConflictStatus(models.TextChoices):
    NO_CONFLICT = NO_CONFLICT_STATUS, _(NO_CONFLICT_STATUS)
    CONFLICT = CONFLICT_STATUS, _(CONFLICT_STATUS)


EXTENSIV_COG_SOURCE = "Extensiv"
DC_COG_SOURCE = "Data Central"
PF_COG_SOURCE = "PF"


def default_priority_sources():
    return {
        EXTENSIV_COG_SOURCE: 1,
        DC_COG_SOURCE: 2,
        PF_COG_SOURCE: 3
    }


class COGSourceSystem(models.TextChoices):
    EXTENSIV = EXTENSIV_COG_SOURCE, _(EXTENSIV_COG_SOURCE)
    DATA_CENTRAL = DC_COG_SOURCE, _(DC_COG_SOURCE)
    PF = PF_COG_SOURCE, _(PF_COG_SOURCE)
