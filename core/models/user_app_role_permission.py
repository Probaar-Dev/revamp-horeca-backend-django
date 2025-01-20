from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from typing import Tuple


class UserAppRolePermission(models.Model):
    """
    Represents a permission that can be assigned to application roles.
    These permissions define what actions users with specific roles can perform.
    """

    permission = models.CharField(
        max_length=64,
        verbose_name=_("permission"),
        help_text=_("The name of the permission"),
        db_index=True,
        unique=True  # Added to prevent duplicate permissions
    )

    class Meta:
        verbose_name = _("app role permission")
        verbose_name_plural = _("app role permissions")
        ordering = ['permission']
        indexes = [
            models.Index(fields=['permission'])
        ]

    def __str__(self) -> str:
        return self.permission

    @property
    def action_list(self) -> Tuple[str, ...]:
        """
        Lists available actions for this permission in the admin interface.

        Returns:
            Tuple of strings representing available actions.
        """
        return ('view', 'change', 'delete')

    def get_absolute_url(self) -> str:
        """
        Returns the URL for viewing this permission in the admin interface.
        """
        return reverse_lazy('panel:userapprolepermission_detail', args=[self.pk])

    def get_roles(self) -> models.QuerySet:
        """
        Get all roles that have this permission.

        Returns:
            QuerySet of UserAppRole instances with this permission.
        """
        return self.app_roles.all()
