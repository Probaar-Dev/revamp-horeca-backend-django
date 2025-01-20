from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from typing import Tuple

from core.models.user_app_role_permission import UserAppRolePermission


class UserAppRole(models.Model):
    """
    Represents a role in the application with associated permissions.
    Used to manage user access and capabilities within the system.
    """

    name = models.CharField(
        max_length=100,
        verbose_name=_("name"),
        help_text=_("The name of the application role"),
        db_index=True
    )

    permissions = models.ManyToManyField(
        UserAppRolePermission,
        verbose_name=_("permissions"),
        related_name="app_roles",
        help_text=_("The permissions associated with this role")
    )

    class Meta:
        verbose_name = _("app role")
        verbose_name_plural = _("app roles")
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def action_list(self) -> Tuple[str, ...]:
        """
        Lists available actions for this role in the admin interface.

        Returns:
            Tuple of strings representing available actions.
        """
        return ('view', 'change', 'delete')

    def get_absolute_url(self) -> str:
        """
        Returns the URL for viewing this role in the admin interface.
        """
        return reverse_lazy('panel:userapprole_detail', args=[self.pk])

    def has_permission(self, permission_name: str) -> bool:
        """
        Check if this role has a specific permission.

        Args:
            permission_name: The name of the permission to check

        Returns:
            bool: True if the role has the permission, False otherwise
        """
        return self.permissions.filter(name=permission_name).exists()
