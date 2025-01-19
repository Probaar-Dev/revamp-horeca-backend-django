from django.db import models
from django.core.exceptions import ValidationError  # Changed from django.forms
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django.urls import reverse

# from shipping.models.district import District


class Address(models.Model):
    country = CountryField(
        verbose_name=_("country"),
        # max_length is handled internally by CountryField
    )
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("city"),
        db_index=True,  # Add index for better performance on frequently queried field
    )
    province = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("province"),
    )
    # district = models.ForeignKey(
    #     District,
    #     null=True,
    #     verbose_name=_("district"),
    #     on_delete=models.PROTECT,
    #     related_name="addresses",  # Add related_name for reverse lookups
    # )
    address_name = models.CharField(
        max_length=200,
        verbose_name=_("address name"),
    )
    detail = models.CharField(
        max_length=200,
        verbose_name=_("address detail"),  # Fixed duplicate verbose name
        null=True,
        blank=True,
    )
    date_creation = models.DateField(  # Changed to DateTimeField for more precision
        verbose_name=_("date creation"),
        auto_now_add=True,
    )
    odoo_id = models.IntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name=_("odoo id"),
        db_index=True,  # Add index for unique field
    )
    schedule_min_1 = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("schedule min 1"),
    )
    schedule_max_1 = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("schedule max 1"),
    )
    schedule_min_2 = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("schedule min 2"),
    )
    schedule_max_2 = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("schedule max 2"),
    )

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")
        ordering = ('address_name',)
        indexes = [
            models.Index(fields=['address_name', 'city']),  # Composite index for common lookups
        ]

    def __str__(self):
        if self.city:
            return f"{self.address_name} - {self.city}, {self.country}"
        return f"{self.address_name}, {self.country}"

    @property
    def action_list(self):
        return ('view', 'change', 'delete')

    def get_absolute_url(self):
        # Changed from reverse_lazy to reverse as it's not needed in model methods
        return reverse('panel:address_detail', args=[self.pk])

    def clean(self):
        super().clean()  # Add super().clean() call
        errors = {}

        if self.schedule_min_1 and self.schedule_max_1:
            if self.schedule_min_1 > self.schedule_max_1:
                errors['schedule_min_1'] = _("Schedule min 1 should be less than schedule max 1")

        if self.schedule_min_2 and self.schedule_max_2:
            if self.schedule_min_2 > self.schedule_max_2:
                errors['schedule_min_2'] = _("Schedule min 2 should be less than schedule max 2")

        if errors:
            raise ValidationError(errors)

    def discard_incomplete_schedules(self):
        if not self.schedule_min_1 or not self.schedule_max_1:
            self.schedule_min_1 = None
            self.schedule_max_1 = None
        if not self.schedule_min_2 or not self.schedule_max_2:
            self.schedule_min_2 = None
            self.schedule_max_2 = None

    def save(self, *args, **kwargs):
        self.full_clean()  # Add validation on save
        self.discard_incomplete_schedules()
        super().save(*args, **kwargs)  # Changed return super() to super()
