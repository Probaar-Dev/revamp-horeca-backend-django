from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db.models.fields.related import ForeignKey
from typing import Any


class Period(models.Model):
    class Weekdays(models.IntegerChoices):
        MONDAY = 0, _("monday")
        TUESDAY = 1, _("tuesday")
        WEDNESDAY = 2, _("wednesday")
        THURSDAY = 3, _("thursday")
        FRIDAY = 4, _("friday")
        SATURDAY = 5, _("saturday")
        SUNDAY = 6, _("sunday")

    place: ForeignKey['Place'] = models.ForeignKey(
        'core.Place',
        editable=False,
        db_index=True,
        on_delete=models.CASCADE,
        verbose_name=_("place"),
        related_name="periods"  # Added for better reverse relationship access
    )

    weekday = models.IntegerField(
        choices=Weekdays.choices,
        verbose_name=_("weekday"),
        db_index=True  # Added for better query performance
    )

    open_time = models.TimeField(
        verbose_name=_("open time"),
        help_text=_("Time when the place opens")
    )

    close_time = models.TimeField(
        verbose_name=_("close time"),
        help_text=_("Time when the place closes")
    )

    class Meta:
        ordering = ['weekday', 'open_time']
        verbose_name = _("period")
        verbose_name_plural = _("periods")
        indexes = [
            models.Index(fields=['weekday', 'open_time']),
        ]

    def __str__(self) -> str:
        return self.get_weekday_display()

    def get_absolute_url(self) -> str:
        return self.place.get_absolute_url()  # Changed from parent to place
