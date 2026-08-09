"""
Authentication models - Custom User and Profile models
"""

from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from phonenumber_field.modelfields import PhoneNumberField
from apps.core.models import BaseModel


class User(AbstractUser):
    """
    Custom User model with role-based authentication
    """
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('vendor', 'Vendor'),
        ('broker', 'Broker'),
        ('admin', 'Admin'),
        ('verification_officer', 'Verification Officer'),
        ('finance_manager', 'Finance Manager'),
        ('super_admin', 'Super Admin'),
    ]

    id = models.UUIDField(primary_key=True, default=models.uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(blank=True, null=True, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    # Remove username, use email instead
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def full_name(self):
        return self.get_full_name()

    def has_role(self, role):
        return self.role == role

    def can_manage_properties(self):
        return self.role in ['vendor', 'broker', 'admin', 'super_admin']

    def can_approve_properties(self):
        return self.role in ['admin', 'super_admin']

    def can_verify_properties(self):
        return self.role in ['verification_officer', 'admin', 'super_admin']


class UserProfile(BaseModel):
    """
    Extended user profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True, max_length=500)
    
    # Location information
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    location = models.PointField(null=True, blank=True, srid=4326)  # GPS coordinates
    
    # Preferences (JSON field for flexibility)
    preferences = models.JSONField(default=dict, blank=True)
    
    # Verification and trust
    verification_score = models.IntegerField(default=0)
    is_identity_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"

    def update_location(self, latitude, longitude):
        """Update user location from coordinates"""
        self.location = Point(longitude, latitude, srid=4326)
        self.save()

    def calculate_verification_score(self):
        """Calculate user verification score (0-100)"""
        score = 0
        if self.is_email_verified:
            score += 25
        if self.is_phone_verified:
            score += 25
        if self.is_identity_verified:
            score += 30
        if self.user.phone:
            score += 10
        if self.bio:
            score += 5
        if self.avatar:
            score += 5
        
        self.verification_score = min(score, 100)
        self.save()
        return self.verification_score


class UserSession(BaseModel):
    """
    Track user sessions for security and analytics
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(max_length=20, blank=True, null=True)  # mobile, desktop, tablet
    location = models.PointField(null=True, blank=True, srid=4326)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'

    def __str__(self):
        return f"Session for {self.user.email} from {self.ip_address}"


class PasswordResetToken(BaseModel):
    """
    Password reset tokens
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=64, unique=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'

    def __str__(self):
        return f"Reset token for {self.user.email}"


class EmailVerificationToken(BaseModel):
    """
    Email verification tokens
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_tokens')
    token = models.CharField(max_length=64, unique=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'email_verification_tokens'
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'

    def __str__(self):
        return f"Email token for {self.user.email}"