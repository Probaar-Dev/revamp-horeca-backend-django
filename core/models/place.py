from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from typing import Tuple, Literal, Optional

from core.models.mixins import get_active_mixin
from core.constants import (
    PLACE_BAR, PLACE_DISCO, PLACE_RESTAURANT, PLACE_STORE,
    PLACE_GENERAL, PLACE_WAREHOUSE,
)


class Place(get_active_mixin()):
    class PlaceType(models.TextChoices):
        BAR = PLACE_BAR, _("bar")
        DISCO = PLACE_DISCO, _("discotek")
        RESTAURANT = PLACE_RESTAURANT, _("restaurant")
        STORE = PLACE_STORE, _("store")
        GENERAL = PLACE_GENERAL, _("general")
        WAREHOUSE = PLACE_WAREHOUSE, _("warehouse")

    org = models.ForeignKey(
        'core.Organization',
        on_delete=models.PROTECT,
        verbose_name=_("organization"),
        related_name="places",
        null=True
    )

    type = models.SlugField(
        choices=PlaceType.choices,
        default=PlaceType.GENERAL,
        verbose_name=_("type"),
        db_index=True
    )

    name = models.CharField(
        max_length=120,
        verbose_name=_("name"),
        db_index=True
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("description")
    )

    phone = models.CharField(
        blank=True,
        null=True,
        max_length=30,
        verbose_name=_("phone")
    )

    address = models.ForeignKey(
        'core.Address',
        on_delete=models.PROTECT,
        verbose_name=_("address"),
        related_name="places"
    )

    portrait = models.ImageField(
        upload_to='core/places/portraits/',
        blank=True,
        null=True,
        verbose_name=_("portrait")
    )

    logo = models.ImageField(
        upload_to='core/places/logos/',
        blank=True,
        null=True,
        verbose_name=_("logo")
    )

    website = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("website")
    )

    dispatch_address = models.BooleanField(
        default=False,
        verbose_name=_("dispatch address"),
        help_text=_("Indicates if this place can be used for dispatching")
    )

    class Meta:
        ordering = ['id']
        verbose_name = _("place")
        verbose_name_plural = _("places")
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['type'])
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def action_list(self) -> Tuple[Literal['view', 'change', 'delete'], ...]:
        return ('view', 'change', 'delete')

    def get_absolute_url(self) -> str:
        return reverse_lazy('panel:place_detail', args=[self.pk])

    def setup(self) -> None:
        """
        Initialize store-specific data if the place is of type store.
        Creates default price and stock entries for all labels.
        """
        if self.type != self.PlaceType.STORE:
            return

        # from inventory.models import Label
        #
        # label_set = Label.objects.all()
        # for label in label_set:
        #     self.price_set.get_or_create(label=label)
        #     self.stock_set.get_or_create(label=label)


@receiver(post_save, sender=Place)
def post_save_place(
        sender: models.Model,
        instance: 'Place',
        created: bool,
        **kwargs
) -> None:
    """
    Post-save signal handler that triggers setup for newly created places.
    """
    if created:
        instance.setup()


@receiver(post_delete, sender=Place)
def post_delete_place(
        sender: models.Model,
        instance: 'Place',
        **kwargs
) -> None:
    """
    Post-delete signal handler that ensures the associated address is deleted.
    """
    if hasattr(instance, 'address') and instance.address is not None:
        try:
            instance.address.delete()
        except Exception:
            pass
