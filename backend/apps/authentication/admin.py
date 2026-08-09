"""
Admin configuration for authentication models
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserSession, PasswordResetToken, EmailVerificationToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin with role-based filtering
    """
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Contact', {'fields': ('phone',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'last_login')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    User Profile admin
    """
    list_display = ('get_user_email', 'city', 'state', 'verification_score', 'is_identity_verified')
    list_filter = ('city', 'state', 'is_identity_verified', 'is_email_verified', 'is_phone_verified')
    search_fields = ('user__email', 'city', 'state')
    readonly_fields = ('verification_score', 'id', 'created_at', 'updated_at')
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Profile Info', {'fields': ('avatar', 'bio', 'city', 'state', 'location')}),
        ('Preferences', {'fields': ('preferences',)}),
        ('Verification', {
            'fields': ('verification_score', 'is_identity_verified', 'is_phone_verified', 'is_email_verified')
        }),
        ('Metadata', {'fields': ('id', 'created_at', 'updated_at')}),
    )

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    User Session admin
    """
    list_display = ('user', 'ip_address', 'device_type', 'is_active', 'created_at')
    list_filter = ('device_type', 'is_active', 'created_at')
    search_fields = ('user__email', 'ip_address')
    readonly_fields = ('session_key', 'id', 'created_at', 'updated_at')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Password Reset Token admin
    """
    list_display = ('user', 'is_used', 'expires_at', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'id', 'created_at', 'updated_at')


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    Email Verification Token admin
    """
    list_display = ('user', 'is_used', 'expires_at', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'id', 'created_at', 'updated_at')