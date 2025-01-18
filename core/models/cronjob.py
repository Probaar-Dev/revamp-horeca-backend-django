from django.db import models
from django.utils.translation import gettext_lazy as _
from typing import Tuple, Literal

# Define job types as Literal types for better type checking
JobTypes = Literal[
    'all_sync_odoo',
    'rebuild_index',
    'compliance_morning',
    'compliance_afternoon'
]

# Constants
ALL_SYNC_ODOO: JobTypes = 'all_sync_odoo'
REBUILD_INDEX: JobTypes = 'rebuild_index'
COMPLIANCE_MORNING: JobTypes = 'compliance_morning'
COMPLIANCE_AFTERNOON: JobTypes = 'compliance_afternoon'

# Type-hinted choices tuple
CHOICES_JOB: Tuple[Tuple[JobTypes, str], ...] = (
    (ALL_SYNC_ODOO, _('all_sync_odoo')),
    (REBUILD_INDEX, _('rebuild_index')),
    (COMPLIANCE_MORNING, _('compliance_morning')),
    (COMPLIANCE_AFTERNOON, _('compliance_afternoon')),
)


class CronJob(models.Model):
    description: str = models.CharField(
        max_length=100,
        verbose_name=_("description"),
        help_text=_("Description of the cron job")
    )
    type: JobTypes = models.CharField(
        verbose_name=_("Cron Job Type"),
        max_length=50,
        choices=CHOICES_JOB,
        help_text=_("Type of cron job to execute")
    )
    is_active: bool = models.BooleanField(
        default=True,
        editable=True,
        verbose_name=_("active"),
        help_text=_("Whether this cron job is active")
    )

    notes: str = models.CharField(
        max_length=100,
        null=True,
        verbose_name=_("notes"),
        help_text=_("Notes of the cron job")
    )

    class Meta:
        ordering = ['type']
        verbose_name = _("Cron Job")
        verbose_name_plural = _("Cron Jobs")
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['is_active']),
        ]

    @property
    def action_list(self) -> Tuple[str, ...]:
        """
        Returns the list of available actions for this cron job.

        Returns:
            Tuple containing the available actions.
        """
        return ('run',)

    def __str__(self) -> str:
        return self.get_type_display()

    def save(self, *args, **kwargs) -> None:
        """Override save to perform any necessary pre-save operations."""
        super().save(*args, **kwargs)
