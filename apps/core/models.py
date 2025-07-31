"""
Core models for the RAG system.
Contains base models and common functionality.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    An abstract base class model that provides a UUID primary key.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, UUIDModel):
    """
    Base model that combines timestamp and UUID functionality.
    """

    class Meta:
        abstract = True


class UserOwnedModel(BaseModel):
    """
    Abstract model for resources owned by users.
    """
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_%(class)s',
        verbose_name=_('Owner')
    )

    class Meta:
        abstract = True


class SharedModel(UserOwnedModel):
    """
    Abstract model for resources that can be shared between users.
    """
    shared_with = models.ManyToManyField(
        User,
        blank=True,
        related_name='shared_%(class)s',
        verbose_name=_('Shared with')
    )

    is_public = models.BooleanField(
        default=False,
        verbose_name=_('Is public'),
        help_text=_('Whether this resource is publicly accessible')
    )

    class Meta:
        abstract = True

    def can_access(self, user):
        """Check if user can access this resource."""
        if not user.is_authenticated:
            return self.is_public

        return (
                self.is_public or
                self.owner == user or
                self.shared_with.filter(id=user.id).exists() or
                user.is_superuser
        )

    def can_edit(self, user):
        """Check if user can edit this resource."""
        if not user.is_authenticated:
            return False

        return self.owner == user or user.is_superuser


class VersionedModel(BaseModel):
    """
    Abstract model that provides versioning capabilities.
    """
    version = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Version')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is active')
    )

    class Meta:
        abstract = True

    def create_new_version(self):
        """Create a new version of this model instance."""
        # Deactivate current version
        self.is_active = False
        self.save()

        # Create new version
        new_instance = self.__class__.objects.get(pk=self.pk)
        new_instance.pk = None
        new_instance.id = None
        new_instance.version += 1
        new_instance.is_active = True
        new_instance.save()

        return new_instance


class StatusChoices(models.TextChoices):
    """Common status choices used across the application."""
    PENDING = 'pending', _('Pending')
    PROCESSING = 'processing', _('Processing')
    COMPLETED = 'completed', _('Completed')
    FAILED = 'failed', _('Failed')
    CANCELLED = 'cancelled', _('Cancelled')


class ProcessingStatusModel(BaseModel):
    """
    Abstract model for tracking processing status of resources.
    """
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        verbose_name=_('Status')
    )

    status_message = models.TextField(
        blank=True,
        verbose_name=_('Status message'),
        help_text=_('Additional information about the current status')
    )

    processing_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Processing started at')
    )

    processing_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Processing completed at')
    )

    class Meta:
        abstract = True

    @property
    def is_processing(self):
        """Check if the resource is currently being processed."""
        return self.status == StatusChoices.PROCESSING

    @property
    def is_completed(self):
        """Check if the processing is completed."""
        return self.status == StatusChoices.COMPLETED

    @property
    def has_failed(self):
        """Check if the processing has failed."""
        return self.status == StatusChoices.FAILED

    def mark_processing(self, message=''):
        """Mark the resource as being processed."""
        from django.utils import timezone

        self.status = StatusChoices.PROCESSING
        self.status_message = message
        self.processing_started_at = timezone.now()
        self.save(update_fields=['status', 'status_message', 'processing_started_at'])

    def mark_completed(self, message=''):
        """Mark the processing as completed."""
        from django.utils import timezone

        self.status = StatusChoices.COMPLETED
        self.status_message = message
        self.processing_completed_at = timezone.now()
        self.save(update_fields=['status', 'status_message', 'processing_completed_at'])

    def mark_failed(self, message=''):
        """Mark the processing as failed."""
        self.status = StatusChoices.FAILED
        self.status_message = message
        self.save(update_fields=['status', 'status_message'])


class MetadataModel(models.Model):
    """
    Abstract model for storing metadata as JSON.
    """
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Metadata'),
        help_text=_('Additional metadata stored as JSON')
    )

    class Meta:
        abstract = True

    def get_metadata(self, key, default=None):
        """Get a metadata value by key."""
        return self.metadata.get(key, default)

    def set_metadata(self, key, value):
        """Set a metadata value."""
        self.metadata[key] = value

    def update_metadata(self, data):
        """Update metadata with a dictionary."""
        self.metadata.update(data)


class SoftDeleteManager(models.Manager):
    """Manager for soft delete functionality."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        """Return all objects including soft deleted ones."""
        return super().get_queryset()

    def deleted_only(self):
        """Return only soft deleted objects."""
        return super().get_queryset().filter(is_deleted=True)


class SoftDeleteModel(models.Model):
    """
    Abstract model that provides soft delete functionality.
    """
    is_deleted = models.BooleanField(
        default=False,
        verbose_name=_('Is deleted')
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Deleted at')
    )

    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete the object."""
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self):
        """Permanently delete the object."""
        super().delete()

    def restore(self):
        """Restore a soft deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])
