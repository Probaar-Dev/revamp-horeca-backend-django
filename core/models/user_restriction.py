from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from typing import Tuple, Any


class UserRestriction(models.Model):
    """
    Represents a restriction on a user's access to specific objects in the system.
    Uses Django's ContentTypes framework to support restrictions on any model type.
    """

    user = models.ForeignKey(
        'core.User',
        on_delete=models.CASCADE,
        verbose_name=_("user"),
        related_name="restrictions",
        help_text=_("The user this restriction applies to")
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("content type"),
        help_text=_("The type of object being restricted"),
        related_name="user_restrictions"
    )

    object_id = models.PositiveIntegerField(
        verbose_name=_("object ID"),
        help_text=_("The ID of the specific object being restricted")
    )

    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    class Meta:
        verbose_name = _("user restriction")
        verbose_name_plural = _("user restrictions")
        indexes = [
            models.Index(fields=['content_type', 'user']),
            models.Index(fields=['object_id']),
        ]
        unique_together = ('content_type', 'user', 'object_id')
        ordering = ['user', 'content_type', 'object_id']

    def __str__(self) -> str:
        return _(
            "Restriction %(object_id)s for user %(user)s in %(content_type)s"
        ) % {
            'object_id': self.object_id,
            'user': self.user,
            'content_type': self.content_type
        }

    @property
    def action_list(self) -> Tuple[str, ...]:
        """
        Lists available actions for this restriction in the admin interface.

        Returns:
            Tuple of strings representing available actions.
        """
        return ('view', 'change', 'delete')

    def get_absolute_url(self) -> str:
        """
        Returns the URL for viewing this restriction in the admin interface.
        """
        return reverse_lazy('panel:user_restriction_detail', args=[self.pk])

    def get_restricted_object(self) -> Any:
        """
        Get the actual object that is being restricted.

        Returns:
            The restricted object instance
        """
        return self.content_object

    @classmethod
    def restrict_user_from_object(
            cls,
            user: 'User',
            obj: Any
    ) -> 'UserRestriction':
        """
        Create a new restriction for a user on a specific object.

        Args:
            user: The user to restrict
            obj: The object to restrict access to

        Returns:
            The created UserRestriction instance
        """
        content_type = ContentType.objects.get_for_model(obj)
        return cls.objects.create(
            user=user,
            content_type=content_type,
            object_id=obj.pk
        )
