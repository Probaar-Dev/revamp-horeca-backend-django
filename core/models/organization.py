from collections import defaultdict
import logging
from typing import List, Optional
from django.core.validators import MinValueValidator
from django.utils.functional import cached_property
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django.urls import reverse_lazy
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from core.models.mixins import get_active_mixin
from core.models.address import Address
from core.models.place import Place
from core.models.user_restriction import UserRestriction
#from inventory.models.odoo_price_list import OdooPriceList
from core.constants import (
    BLOCK_REASON_GENERAL, BLOCK_REASON_PAYMENT, BLOCK_REASON_VERIFICATION_PENDING,
    EXTRA_DAYS_FOR_DUE_INVOICES, UNBLOCK_REASON_PAYMENT, UNBLOCK_REASON_TEMPORAL_UNBLOCK,
)


class Organization(get_active_mixin()):
    class OrgType(models.TextChoices):
        BUSINESS = 'BUSINESS', _('org_type_business')
        PERSON = 'PERSON', _('org_type_person')

    class DocumentType(models.TextChoices):
        DNI = 'DNI', 'DNI'
        RUC = 'RUC', 'RUC'

    class BlockReason(models.TextChoices):
        GENERAL = BLOCK_REASON_GENERAL, _("block_reason_general")
        PAYMENT = BLOCK_REASON_PAYMENT, _("block_reason_payment")
        VERIFICATION_PENDING = BLOCK_REASON_VERIFICATION_PENDING, _("block_reason_verification_pending")

    class UnblockReason(models.TextChoices):
        PAYMENT = UNBLOCK_REASON_PAYMENT, _("unblock_reason_payment")
        TEMPORAL = UNBLOCK_REASON_TEMPORAL_UNBLOCK, _("unblock_reason_temporal_unblock")

    AUTOGENERATE_ORGCODE = '__autogenerate__'

    # Blocking related fields
    blocked = models.BooleanField(
        default=False,
        verbose_name=_('blocked'),
        db_index=True
    )

    blocking_reason = models.SlugField(
        choices=BlockReason.choices,
        verbose_name=_("Blocking Reason"),
        null=True,
        blank=True,
        db_index=True
    )

    unblocking_reason = models.SlugField(
        choices=UnblockReason.choices,
        verbose_name=_("Unblocking Reason"),
        null=True,
        blank=True
    )

    # Organization details
    # price_list = models.ForeignKey(
    #     OdooPriceList,
    #     on_delete=models.PROTECT,
    #     verbose_name=_("price list"),
    #     related_name="organizations"
    # )

    payment_term = models.CharField(
        max_length=100,
        verbose_name=_("payment term"),
        null=True,
        help_text=_("Payment terms for this organization")
    )

    payment_term_days = models.PositiveIntegerField(
        verbose_name=_("payment term days"),
        default=0,
        validators=[MinValueValidator(0)]
    )

    type = models.CharField(
        max_length=8,
        choices=OrgType.choices,
        verbose_name=_("type"),
        db_index=True
    )

    orgcode = models.CharField(
        max_length=45,
        unique=True,
        verbose_name=_("orgcode"),
        help_text=_("example: probaar.co"),
        blank=True,
        db_index=True
    )

    # Name fields
    commercial_name = models.CharField(
        max_length=100,
        verbose_name=_("commercial name"),
        blank=True
    )

    legal_name = models.CharField(
        max_length=100,
        verbose_name=_("legal name"),
        blank=True,
        db_index=True
    )

    first_name = models.CharField(
        max_length=100,
        verbose_name=_("first name"),
        blank=True
    )

    last_name = models.CharField(
        max_length=100,
        verbose_name=_("last name"),
        blank=True
    )

    # Document fields
    country = CountryField(
        verbose_name=_("country"),
        db_index=True
    )

    document_type = models.CharField(
        max_length=3,
        choices=DocumentType.choices,
        verbose_name=_("document type")
    )

    document_number = models.CharField(
        max_length=20,
        verbose_name=_("document number"),
        unique=True,
        db_index=True
    )

    # Dates and addresses
    date_creation = models.DateField(
        verbose_name=_("date creation"),
        auto_now_add=True,
        blank=True,
        db_index=True
    )

    fiscal_address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        verbose_name=_("fiscal address"),
        null=True,
        blank=True,
        related_name='fiscal_organizations'
    )

    default_shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        verbose_name=_("default shipping address"),
        related_name='default_shipping_organizations',
        null=True,
        blank=True
    )

    # Business rules
    min_order_amount = models.IntegerField(
        verbose_name=_("min order amount"),
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    days_before_blocking = models.PositiveIntegerField(
        default=EXTRA_DAYS_FOR_DUE_INVOICES,
        validators=[MinValueValidator(1)],
        verbose_name=_("days_before_blocking")
    )

    # External IDs
    odoo_partner_id = models.IntegerField(
        verbose_name=_("Odoo Partner ID"),
        null=True,
        blank=True,
        db_index=True
    )

    cluster_odoo_id = models.IntegerField(
        verbose_name=_("Cluster ID"),
        null=True,
        blank=True
    )

    cluster_odoo_name = models.CharField(
        max_length=100,
        verbose_name=_("Cluster Name"),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")
        ordering = ['legal_name', 'first_name']
        indexes = [
            models.Index(fields=['legal_name', 'first_name']),
            models.Index(fields=['type', 'document_number']),
        ]

    def __str__(self) -> str:
        if self.type == self.OrgType.PERSON and self.get_full_name():
            return f"{self.get_full_name()} - {self.orgcode}"
        return f"{self.legal_name} - {self.orgcode}"

    def get_full_name(self) -> str:
        """Returns the full name based on organization type."""
        if self.type == self.OrgType.PERSON:
            return f"{self.first_name} {self.last_name}".strip()
        return self.legal_name

    @property
    def action_list(self) -> tuple[str, ...]:
        return ('view', 'change', 'delete')

    def get_absolute_url(self) -> str:
        return reverse_lazy('panel:organization_detail', args=[self.pk])

    def is_blocked(self) -> bool:
        return self.blocked

    def is_temporarily_unblocked(self) -> bool:
        """Check if the organization is temporarily unblocked."""
        return not self.blocked and self.unblocking_reason == self.UnblockReason.TEMPORAL

    def trigger_blocking_reason(self) -> None:
        """Update blocking reason based on blocked status."""
        if not self.blocked:
            self.blocking_reason = None
        elif self.blocked and not self.blocking_reason:
            self.blocking_reason = self.BlockReason.PAYMENT

    def set_blocking_status_by_due_invoices(self, due_invoices: int) -> bool:
        """Set blocking status based on number of due invoices."""
        if due_invoices > 0:
            return self.block(blocking_reason=self.BlockReason.PAYMENT)
        return self.unblock(unblocking_reason=self.UnblockReason.PAYMENT)

    def get_active_users(self):
        """Get all active users associated with this organization."""
        return self.user_model.objects.filter(
            organizationmembership__organization=self,
            is_active=True
        ).all()

    def get_active_user_emails(self, for_odoo_address_id: Optional[int] = None) -> List[str]:
        """
        Returns the list of emails for the active users of the organization.

        Args:
            for_odoo_address_id: if provided, only users with access to this odoo address will be returned.

        Returns:
            List of email addresses for active users.
        """
        if not for_odoo_address_id:
            filtered_users_id = []
        elif not Place.objects.filter(org=self, address__odoo_id=for_odoo_address_id).exists():
            logging.warning(
                'Organization.get_active_user_emails called with invalid '
                f'for_odoo_address_id={for_odoo_address_id} (org_id={self.pk}). '
                'Ignoring filters.'
            )
            filtered_users_id = []
        else:
            try:
                org_place_restrictions = UserRestriction.objects.filter(
                    content_type=ContentType.objects.get_for_model(Place),
                    user__organizations=self
                )

                user_place_restrictions_map = defaultdict(list)
                for restriction in org_place_restrictions:
                    odoo_address_id = Place.objects.filter(
                        id=restriction.object_id
                    ).values_list('address__odoo_id', flat=True).first()
                    user_place_restrictions_map[restriction.user_id].append(odoo_address_id)

                filtered_users_id = [
                    user_id for user_id in user_place_restrictions_map
                    if for_odoo_address_id not in user_place_restrictions_map[user_id]
                ]
            except Exception as e:
                logging.exception(
                    f'Organization.get_active_user_emails failed to retrieve user '
                    f'restrictions for org_id={self.pk}. Ignoring filters.'
                )
                filtered_users_id = []

        emails = list(
            self.user_model.objects.filter(
                organizationmembership__organization=self,
                is_active=True
            ).exclude(
                id__in=filtered_users_id
            ).values_list('email', flat=True)
        )
        return [email for email in emails if email and email.strip()]

    def dispatch_places(self):
        """Get all active dispatch places for this organization."""
        return self.place_set.select_related('address').filter(
            is_active=True,
            dispatch_address=True
        ).all()

    def get_shipping_addresses(self) -> List[Address]:
        """Get all shipping addresses from dispatch places."""
        return [p.address for p in self.dispatch_places()]

    def shipping_address_from_address_id(self, address_id: int) -> Address:
        """
        Get shipping address by ID.

        Raises:
            AttributeError: If no matching active dispatch place is found
        """
        place = self.place_set.select_related('address').filter(
            address_id=address_id,
            dispatch_address=True,
            is_active=True
        ).first()
        return place.address  # Raises AttributeError if place is None

    def has_address(self, address: Address) -> bool:
        """Check if organization has an active place with given address."""
        return self.place_set.filter(
            address=address,
            is_active=True
        ).exists()

    def block(self, blocking_reason: str = BlockReason.PAYMENT) -> bool:
        """Block the organization with given reason."""
        if not self.is_blocked():
            self.blocked = True
            self.blocking_reason = blocking_reason
            self.unblocking_reason = None
            self.save(update_fields=['blocked', 'blocking_reason', 'unblocking_reason'])
            return True
        return False

    def unblock(self, unblocking_reason: str = UnblockReason.PAYMENT) -> bool:
        """
        Unblock the organization.
        Returns True if organization was blocked or temporarily unblocked.
        """
        if self.is_blocked() or self.unblocking_reason == self.UnblockReason.TEMPORAL:
            self.blocked = False
            self.unblocking_reason = unblocking_reason
            self.blocking_reason = None
            self.save(update_fields=['blocked', 'unblocking_reason', 'blocking_reason'])
            return True
        return False

    def check_autogenerate_orgcode(self) -> None:
        """Generate orgcode if using placeholder value."""
        if self.orgcode == self.AUTOGENERATE_ORGCODE:
            self.orgcode = f'organization_{self.pk}'
            self.save(update_fields=['orgcode'])

    @cached_property
    def user_model(self):
        """Get the user model configured for the project."""
        return get_user_model()


@receiver(pre_save, sender=Organization)
def pre_save_organization(
        sender: models.Model,
        instance: Organization,
        **kwargs
) -> None:
    """Ensure blocking reason is properly set before saving."""
    instance.trigger_blocking_reason()


@receiver(post_save, sender=Organization)
def post_save_organization(
        sender: models.Model,
        instance: Organization,
        **kwargs
) -> None:
    """Handle post-save operations like orgcode generation."""
    instance.check_autogenerate_orgcode()

