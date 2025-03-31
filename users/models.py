from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone as django_timezone
from zoneinfo import ZoneInfo, available_timezones


class CustomUserManager(BaseUserManager):
    """Define a model manager for CustomUser model with email instead of username."""

    def _create_user(self, email, name, password, **extra_fields):
        """Create and save a user with the given email, name and password."""
        if not email:
            raise ValueError('The email must be set')
        if not name:
            raise ValueError('The name must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, name, password, **extra_fields)

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, name, password, **extra_fields)


# Get common timezones for choices
TIMEZONE_CHOICES = [(tz, tz) for tz in sorted(available_timezones())]


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom user model that uses email instead of username"""
    email = models.EmailField('email address', unique=True)
    name = models.CharField('name', max_length=150)
    timezone = models.CharField('timezone', max_length=50, choices=TIMEZONE_CHOICES, default='UTC')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=django_timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
        
    def get_timezone(self):
        """Return the user's timezone as a ZoneInfo object"""
        return ZoneInfo(self.timezone)
