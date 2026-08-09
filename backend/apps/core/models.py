"""
Core models - Base classes for other models
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model


class BaseModel(models.Model):
    """
    Abstract base model with common fields
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditableModel(BaseModel):
    """
    Abstract model that tracks who created/updated the record
    """
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract model for soft deletion
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted'
    )

    class Meta:
        abstract = True


class TimestampedModel(BaseModel, SoftDeleteModel, AuditableModel):
    """
    Complete base model with timestamps, audit trail, and soft deletion
    """
    
    class Meta:
        abstract = True