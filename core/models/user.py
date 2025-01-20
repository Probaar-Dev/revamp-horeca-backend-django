from typing import Optional, List, Tuple, Any
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.tokens import default_token_generator
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.functional import cached_property
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from core.models.organization import Organization
from core.models.organization_membership import OrganizationMembership
from core.models.place import Place
from core.models.user_restriction import UserRestriction
from core.constants import (
    GENDER_FEMALE, GENDER_MALE, GENDER_OTHER, LEVEL_ERROR, LEVEL_SUCCESS,
    SHOW_ONBOARDING_MODAL_TRUE, SHOW_ONBOARDING_MODAL_FALSE,
)


class CustomUserManager(UserManager):
    """
    Custom manager that prefetches related fields to optimize database queries.
    """

    def get(self, *args, **kwargs) -> 'User':
        return super().prefetch_related(
            'organizations',  # Used in /api/search view to filter results
            'organizations__price_list',  # Used for price list filtering
            'organizationmembership_set',
        ).get(*args, **kwargs)


class User(AbstractUser):
    """
    Custom user model with extended functionality for organization management
    and user preferences.
    """
    class Meta:
        ordering = ['first_name', 'username']
        verbose_name = _("user")
        verbose_name_plural = _("users")
        indexes = [
            models.Index(fields=['first_name', 'username']),
            models.Index(fields=['email']),
        ]

    # Override groups field from AbstractUser to add related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="core_user_set",  # Changed from default 'user_set'
        related_query_name="core_user",
    )

    # Override user_permissions field from AbstractUser to add related_name
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="core_user_set",  # Changed from default 'user_set'
        related_query_name="core_user",
    )

    class Gender(models.TextChoices):
        MALE = GENDER_MALE, _("male")
        FEMALE = GENDER_FEMALE, _("female")
        OTHER = GENDER_OTHER, _("other")

    class OnboardingModalStatus(models.TextChoices):
        SHOW = SHOW_ONBOARDING_MODAL_TRUE, _("true")
        HIDE = SHOW_ONBOARDING_MODAL_FALSE, _("false")

    objects = CustomUserManager()

    # Organization relationships
    organizations = models.ManyToManyField(
        'core.Organization',
        through='core.OrganizationMembership',
        blank=True,
        verbose_name=_("organizations"),
        related_name='users',
        help_text=_("Organizations this user belongs to")
    )

    legacy_logged_org = models.ForeignKey(
        'core.Organization',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("logged organization"),
        help_text=_("Legacy field for storing the last logged organization")
    )

    # User profile fields
    gender = models.SlugField(
        blank=True,
        null=True,
        choices=Gender.choices,
        default=Gender.OTHER,
        verbose_name=_("gender"),
        db_index=True
    )

    show_onboarding_modal = models.SlugField(
        choices=OnboardingModalStatus.choices,
        default=OnboardingModalStatus.HIDE,
        verbose_name=_("show onboarding modal"),
        help_text=_("Controls visibility of the onboarding modal")
    )

    cellphone = models.CharField(
        blank=True,
        null=True,
        max_length=30,
        verbose_name=_("cellphone")
    )

    city = models.CharField(
        blank=True,
        null=True,
        max_length=100,
        verbose_name=_("city"),
        db_index=True
    )

    country = CountryField(
        blank=True,
        null=True,
        verbose_name=_("country"),
        db_index=True
    )

    # Authentication fields
    token = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("token"),
        help_text=_("Authentication token for password reset")
    )

    date_token = models.DateTimeField(
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("token creation date")
    )

    # Relations and preferences
    # categories = models.ManyToManyField(
    #     'inventory.Category',
    #     blank=True,
    #     verbose_name=_("categories"),
    #     help_text=_("Categories of interest for this user")
    # )

    last_date_view_banner = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("last view date of banner"),
        help_text=_("Tracks when the user last saw the banner")
    )

    class Meta:
        ordering = ['first_name', 'username']
        verbose_name = _("user")
        verbose_name_plural = _("users")
        indexes = [
            models.Index(fields=['first_name', 'username']),
            models.Index(fields=['email']),
        ]

    def __init__(self, *args, **kwargs):
        self.__jwt_org_id: Optional[int] = None
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        if self.get_full_name():
            return f'{self.get_full_name()} - {self.username}'
        return self.username

    @property
    def jwt_org_id(self) -> Optional[int]:
        """
        Stores the 'org' claim from the JWT token.

        Returns:
            Optional[int]: None if user is not authenticated or using legacy token
        """
        return self.__jwt_org_id

    @jwt_org_id.setter
    def jwt_org_id(self, value: Optional[int]) -> None:
        self.__jwt_org_id = value

    @cached_property
    def logged_org(self) -> Optional[Organization]:
        """
        Get the currently logged organization for this user.

        Priority order:
        1. JWT 'org' claim if it exists
        2. legacy_logged_org if it exists
        3. First available organization as fallback

        Returns:
            Optional[Organization]: The current organization or None
        """
        if self.__jwt_org_id:
            org_to_return = Organization.objects.get(id=self.__jwt_org_id)
        else:
            if not self.legacy_logged_org:
                self.legacy_logged_org = self.first_available_organization()
                self.save(update_fields=['legacy_logged_org'])
            org_to_return = self.legacy_logged_org

        # Validate user membership
        is_valid_member = OrganizationMembership.objects.filter(
            organization=org_to_return,
            user=self
        ).exists()

        if not is_valid_member:
            org_to_return = self.first_available_organization()
            self.save(update_fields=['legacy_logged_org'])

        return org_to_return

    def get_app_role_for_logged_org(self):
        """Get user's role in the currently logged organization."""
        try:
            return self.organizationmembership_set.get(
                organization=self.logged_org
            ).app_role
        except ObjectDoesNotExist:
            return None

    def get_price_list_for_logged_org(self):
        """Get price list for the currently logged organization."""
        return self.logged_org.price_list if self.logged_org else None

    @property
    def action_list(self) -> Tuple[str, ...]:
        """Available actions for this user in the admin interface."""
        return ('view', 'change', 'delete')

    def get_absolute_url(self) -> str:
        """Get URL for viewing this user in the admin interface."""
        return reverse_lazy('panel:user_detail', args=[self.pk])

    def get_token(self) -> str:
        """Generate a new authentication token for this user."""
        return default_token_generator.make_token(self)

    def get_uid(self) -> str:
        """Get URL-safe base64 encoded user ID."""
        return urlsafe_base64_encode(force_bytes(self.pk))

    def has_available_organizations(self) -> bool:
        """Check if user has any active organizations."""
        return self.organizations.filter(is_active=True).exists()

    def first_available_organization(self) -> Optional[Organization]:
        """Get the first active organization for this user."""
        return self.organizations.filter(is_active=True).first()

    def send_activation_email(self) -> Tuple[str, str]:
        """
        Send account activation email to the user.

        Returns:
            Tuple[str, str]: Status level and message
        """
        if self.is_active:
            return LEVEL_ERROR, _("User is active already.")

        message = self.objects.create_email_from_template(
            template_name="public/account/account_activate.html",
            context={'object': self},
            subject=_("Activate your account"),
            to_email=self.email,
        )

        level, msg = message.send()

        if level == LEVEL_ERROR:
            return LEVEL_ERROR, _('An error has occurred. Login to receive an activation link.')
        return LEVEL_SUCCESS, _(
            'An activation email has been sent to your email "%(email)s". '
            'Please click on the activation link.'
        ) % {'email': self.email}

    def set_active(self) -> Tuple[str, str]:
        """
        Activate the user account.

        Returns:
            Tuple[str, str]: Status level and message
        """
        if self.is_active:
            return LEVEL_ERROR, _("Account is active already.")
        self.is_active = True
        self.save(update_fields=['is_active'])
        return LEVEL_SUCCESS, _("Account has been activated successfully.")

    def set_token(self, force: bool = False) -> Tuple[str, str]:
        """
        Set authentication token for the user.

        Args:
            force: If True, overwrites existing token

        Returns:
            Tuple[str, str]: Status level and message
        """
        if self.token and not force:
            return LEVEL_ERROR, _("User has a token already.")
        self.token = self.get_token()
        self.date_token = timezone.now()
        self.save(update_fields=['token', 'date_token'])
        return LEVEL_SUCCESS, _("Token set successfully.")

    def get_restricted_places_ids(self) -> List[int]:
        """Get IDs of places this user is restricted from accessing."""
        return list(UserRestriction.objects.filter(
            user=self,
            content_type=ContentType.objects.get_for_model(Place)
        ).values_list('object_id', flat=True))

    def get_restricted_addresses_ids(self) -> List[int]:
        """Get IDs of addresses this user is restricted from accessing."""
        restricted_places = self.get_restricted_places_ids()
        return list(Place.objects.filter(
            id__in=restricted_places
        ).values_list('address', flat=True))

    def get_restricted_odoo_addresses_ids(self) -> List[int]:
        """Get Odoo IDs of addresses this user is restricted from accessing."""
        restricted_places = self.get_restricted_places_ids()
        return list(Place.objects.filter(
            id__in=restricted_places
        ).values_list('address__odoo_id', flat=True))


@receiver(post_save, sender=User)
def post_save_user(
        sender: models.Model,
        instance: User,
        created: bool,
        **kwargs
) -> None:
    """
    Send activation email when a new inactive user is created.
    """
    if created and not instance.is_active:
        instance.send_activation_email()