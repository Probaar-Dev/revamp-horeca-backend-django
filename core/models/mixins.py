from typing import Tuple, Optional, Dict
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.base import ModelBase

from core.constants import LEVEL_SUCCESS, LEVEL_ERROR

MessageType = Tuple[str, str]


def get_active_mixin(
    default: bool = True,
    editable: bool = True,
    error_messages: Optional[Dict[str, str]] = None
) -> ModelBase:

    DEFAULT_MESSAGES = {
        'active_already': _("Instance is active already"),
        'inactive_already': _("Instance is inactive already"),
        'set_active': _("Instance is now active."),
        'set_inactive': _("Instance is now inactive."),
    }

    class Model(models.Model):
        is_active = models.BooleanField(
            default=default,
            editable=editable,
            verbose_name=_("active"),
            help_text=_("Indicates if this instance is currently active"),
            db_index=True  # Added for better query performance
        )

        class Meta:
            abstract = True

        def set_active(self) -> MessageType:
            if self.is_active:
                return LEVEL_ERROR, DEFAULT_MESSAGES['active_already']
            self.is_active = True
            self.save(update_fields=['is_active'])
            return LEVEL_SUCCESS, DEFAULT_MESSAGES['set_active']

        def set_inactive(self) -> MessageType:
            if not self.is_active:
                return LEVEL_ERROR, DEFAULT_MESSAGES['inactive_already']
            self.is_active = False
            self.save(update_fields=['is_active'])
            return LEVEL_SUCCESS, DEFAULT_MESSAGES['set_inactive']

        def toggle_active(self) -> MessageType:
            return self.set_inactive() if self.is_active else self.set_active()

    return Model


def pre_save_date_deactivation(
    sender: ModelBase,
    instance: models.Model,
    **kwargs
) -> None:
    """
    Pre-save signal handler to manage deactivation dates.
    Should be connected using:
    @receiver(pre_save, sender=YourModel)
    """
    if instance.is_active and instance.date_deactivation:
        instance.date_deactivation = None
    elif not instance.is_active and not instance.date_deactivation:
        instance.date_deactivation = timezone.now()
