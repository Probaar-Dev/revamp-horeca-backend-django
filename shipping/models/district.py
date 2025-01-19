from datetime import date
from functools import cached_property
from itertools import chain
from django.contrib.gis.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator


class District(models.Model):
    ubigeo = models.CharField(
        max_length=80,
        db_index=True,
        validators=[MinLengthValidator(6)]  # Standard UBIGEO length
    )
    name = models.CharField(
        max_length=80,
        db_index=True
    )
    capital = models.CharField(
        max_length=80,
        db_index=True
    )
    department = models.CharField(
        max_length=80,
        db_index=True
    )
    province = models.CharField(
        max_length=80,
        db_index=True
    )
    geom = models.MultiPolygonField(
        srid=4326,
        spatial_index=True
    )
    odoo_id = models.IntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name=_("odoo id"),
        db_index=True
    )

    class Meta:
        verbose_name = _('District')
        verbose_name_plural = _('Districts')
        ordering = ['department', 'province', 'name']
        indexes = [
            models.Index(fields=['department', 'province', 'name']),
            models.Index(fields=['ubigeo']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['department', 'province', 'name'],
                name='unique_district_location'
            )
        ]

    def __str__(self):
        return f"{self.department} - {self.province} - {self.name}"

    def displayable_name(self):
        """Returns the district name in Title Case format."""
        return ' '.join(word.capitalize() for word in self.name.split())

    @property
    def action_list(self):
        return ('view', 'change')

    def get_absolute_url(self):
        return reverse('panel:district_detail', args=[self.pk])

    @cached_property
    def shipping_days(self) -> set[str]:
        """
        Cache the shipping days for this district.
        Returns an empty set if no shipping days are defined.
        """
        return set(
            chain.from_iterable(
                self.groups.values_list('shipping_days', flat=True).distinct()
            )
        )

    def can_ship_in_day(self, shipping_date: date) -> bool:
        """
        Determines if shipping is possible on the given date.

        Args:
            shipping_date: The date to check for shipping availability

        Returns:
            bool: True if shipping is possible, False otherwise.
            Returns True if no shipping days are defined for this district.
        """
        if not self.shipping_days:
            return True

        return shipping_date.strftime('%A').lower() in self.shipping_days


# LayerMapping configuration for GeoDjango
district_mapping = {
    'ubigeo': 'ubigeo',
    'name': 'name',
    'capital': 'capital',
    'department': 'department',
    'province': 'province',
    'geom': 'MULTIPOLYGON',
}