from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from typing import Tuple, Literal

from core.models.mixins import get_active_mixin


class Unit(get_active_mixin()):
    name = models.CharField(
        max_length=50,
        verbose_name=_("name"),
        db_index=True
    )

    short_name = models.CharField(
        max_length=10,
        verbose_name=_("short name"),
        help_text=_("Abbreviated version of the unit name")
    )

    class Meta:
        ordering = ['name']
        verbose_name = _("unit")  # Fixed missing translation wrapper
        verbose_name_plural = _("units")
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def action_list(self) -> Tuple[Literal['view', 'change', 'delete'], ...]:
        return ('view', 'change', 'delete')

    def get_absolute_url(self) -> str:
        return reverse_lazy('panel:unit_detail', args=[self.pk])

    def setup(self) -> None:
        """
        Triggers a save on all associated labels to update their derived data.
        """
        for label in self.label_set.all():
            label.save()


@receiver(post_save, sender=Unit)
def post_save_unit(
        sender: models.Model,
        instance: 'Unit',
        created: bool,
        **kwargs
) -> None:
    """
    Post-save signal handler that triggers setup for all units.
    This updates all associated labels.
    """
    instance.setup()
