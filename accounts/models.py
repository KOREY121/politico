from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models



class VoterManager(BaseUserManager):

    def get_by_natural_key(self, national_id):
        return self.get(**{self.model.USERNAME_FIELD: national_id})

    def create_user(self, national_id, full_name, email, dob, password=None, **extra_fields):
        if not national_id:
            raise ValueError('National ID is required')
        if not email:
            raise ValueError('Email is required')

        email = self.normalize_email(email)
        user  = self.model(
            national_id = national_id,
            full_name   = full_name,
            email       = email,
            dob         = dob,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db) 
        return user

    def create_superuser(self, national_id, full_name, email, dob, password=None, **extra_fields):
        extra_fields.setdefault('is_staff',     True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active',    True)
        extra_fields.setdefault('status',       'active')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(national_id, full_name, email, dob, password, **extra_fields)


class Voter(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = [
        ('active',   'Active'),
        ('inactive', 'Inactive'),
    ]

    voter_id    = models.AutoField(primary_key=True)
    national_id = models.CharField(max_length=50, unique=True)
    full_name   = models.CharField(max_length=255)
    dob         = models.DateField()
    email       = models.EmailField(unique=True)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    
    objects = VoterManager()

    USERNAME_FIELD  = 'national_id'
    REQUIRED_FIELDS = ['full_name', 'email', 'dob']

    class Meta:
        db_table = 'voters'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.full_name} ({self.national_id})"

    def save(self, *args, **kwargs):
        # Sync is_active with status
        if self.status:
            self.is_active = (self.status == 'active')
        super().save(*args, **kwargs)