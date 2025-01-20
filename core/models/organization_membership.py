from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from typing import Optional

from core.models.organization import Organization
from core.models.user_app_role import UserAppRole


class OrganizationMembership(models.Model):
    """
    Represents a membership relationship between a user and an organization,
    optionally including an application role.
    """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name=_("organization"),
        related_name="memberships",
        help_text=_("The organization this membership belongs to")
    )

    user = models.ForeignKey(
        'core.user',
        on_delete=models.CASCADE,
        verbose_name=_("user"),
        related_name="organization_memberships",
        help_text=_("The user who is a member of the organization")
    )

    app_role = models.ForeignKey(
        UserAppRole,
        on_delete=models.PROTECT,
        verbose_name=_("role"),
        null=True,
        blank=True,
        related_name="memberships",
        help_text=_("The role of the user within the organization")
    )

    class Meta:
        verbose_name = _("organization membership")
        verbose_name_plural = _("organization memberships")
        unique_together = ('organization', 'user')
        indexes = [
            models.Index(fields=['organization', 'user']),
            models.Index(fields=['user', 'app_role'])
        ]
        ordering = ['organization', 'user']

    def __str__(self) -> str:
        return f"{self.user} - {self.organization}"
