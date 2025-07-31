"""
User models for the RAG system.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel, MetadataModel


class User(AbstractUser, BaseModel, MetadataModel):
    """
    Custom user model with additional fields for the RAG system.
    """
    email = models.EmailField(
        _('Email address'),
        unique=True,
        help_text=_('Required. Enter a valid email address.')
    )

    first_name = models.CharField(
        _('First name'),
        max_length=150,
        blank=True
    )

    last_name = models.CharField(
        _('Last name'),
        max_length=150,
        blank=True
    )

    bio = models.TextField(
        _('Biography'),
        max_length=500,
        blank=True,
        help_text=_('Optional biography or description')
    )

    avatar = models.ImageField(
        _('Avatar'),
        upload_to='avatars/',
        blank=True,
        null=True
    )

    is_verified = models.BooleanField(
        _('Is verified'),
        default=False,
        help_text=_('Designates whether this user has verified their email address.')
    )

    preferred_language = models.CharField(
        _('Preferred language'),
        max_length=10,
        choices=[
            ('en', _('English')),
            ('fr', _('French')),
            ('de', _('German')),
            ('nl', _('Dutch')),
        ],
        default='en'
    )

    timezone = models.CharField(
        _('Timezone'),
        max_length=50,
        default='UTC',
        help_text=_('User timezone for date/time display')
    )

    # API and usage limits
    api_key = models.CharField(
        _('API Key'),
        max_length=255,
        blank=True,
        unique=True,
        null=True,
        help_text=_('API key for accessing the system programmatically')
    )

    monthly_token_limit = models.PositiveIntegerField(
        _('Monthly token limit'),
        default=100000,
        help_text=_('Maximum number of tokens that can be used per month')
    )

    monthly_tokens_used = models.PositiveIntegerField(
        _('Monthly tokens used'),
        default=0,
        help_text=_('Number of tokens used this month')
    )

    last_token_reset = models.DateTimeField(
        _('Last token reset'),
        auto_now_add=True,
        help_text=_('Last time the monthly token counter was reset')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'users_user'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def display_name(self):
        """Return a display name for the user."""
        if self.full_name:
            return self.full_name
        return self.username or self.email

    def has_api_access(self):
        """Check if user has API access."""
        return bool(self.api_key) and self.is_active

    def can_use_tokens(self, num_tokens):
        """Check if user can use a certain number of tokens."""
        return (self.monthly_tokens_used + num_tokens) <= self.monthly_token_limit

    def use_tokens(self, num_tokens):
        """Deduct tokens from user's monthly limit."""
        if self.can_use_tokens(num_tokens):
            self.monthly_tokens_used += num_tokens
            self.save(update_fields=['monthly_tokens_used'])
            return True
        return False

    def reset_monthly_tokens(self):
        """Reset monthly token usage."""
        from django.utils import timezone

        self.monthly_tokens_used = 0
        self.last_token_reset = timezone.now()
        self.save(update_fields=['monthly_tokens_used', 'last_token_reset'])

    def generate_api_key(self):
        """Generate a new API key for the user."""
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
        self.api_key = f"rag_{api_key}"
        self.save(update_fields=['api_key'])
        return self.api_key


class UserProfile(BaseModel):
    """
    Extended user profile with additional preferences.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # RAG System Preferences
    default_embedding_model = models.CharField(
        _('Default embedding model'),
        max_length=100,
        default='nomic-embed-text',
        help_text=_('Default embedding model to use for new knowledge bases')
    )

    default_llm_model = models.CharField(
        _('Default LLM model'),
        max_length=100,
        default='llama3:8b',
        help_text=_('Default LLM model to use for chat and generation')
    )

    default_chunk_size = models.PositiveIntegerField(
        _('Default chunk size'),
        default=1000,
        help_text=_('Default chunk size for document processing')
    )

    default_chunk_overlap = models.PositiveIntegerField(
        _('Default chunk overlap'),
        default=200,
        help_text=_('Default overlap between chunks')
    )

    # UI Preferences
    theme = models.CharField(
        _('Theme'),
        max_length=20,
        choices=[
            ('light', _('Light')),
            ('dark', _('Dark')),
            ('auto', _('Auto')),
        ],
        default='auto'
    )

    notifications_enabled = models.BooleanField(
        _('Notifications enabled'),
        default=True,
        help_text=_('Whether to receive system notifications')
    )

    email_notifications = models.BooleanField(
        _('Email notifications'),
        default=True,
        help_text=_('Whether to receive email notifications')
    )

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        db_table = 'users_profile'

    def __str__(self):
        return f"{self.user.display_name}'s Profile"


class UserSession(BaseModel):
    """
    Track user sessions and activity.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions'
    )

    session_key = models.CharField(
        _('Session key'),
        max_length=40,
        unique=True
    )

    ip_address = models.GenericIPAddressField(
        _('IP address'),
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        _('User agent'),
        blank=True
    )

    is_active = models.BooleanField(
        _('Is active'),
        default=True
    )

    last_activity = models.DateTimeField(
        _('Last activity'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        db_table = 'users_session'
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.display_name} - {self.session_key[:10]}..."
