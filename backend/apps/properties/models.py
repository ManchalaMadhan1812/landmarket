"""
Property models for LandMarket
"""

import uuid
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimestampedModel, BaseModel

User = get_user_model()

# Choice constants
PROPERTY_TYPE_CHOICES = [
    ('residential', 'Residential'),
    ('commercial', 'Commercial'),
    ('agricultural', 'Agricultural'),
    ('industrial', 'Industrial'),
    ('plot', 'Plot'),
    ('apartment', 'Apartment'),
    ('house', 'House'),
]

PURPOSE_CHOICES = [
    ('sale', 'Sale'),
    ('rent', 'Rent'),
    ('lease', 'Lease'),
]

STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('pending', 'Pending Approval'),
    ('active', 'Active'),
    ('reserved', 'Reserved'),
    ('sold', 'Sold'),
    ('rejected', 'Rejected'),
    ('archived', 'Archived'),
]

AREA_UNIT_CHOICES = [
    ('sqft', 'Square Feet'),
    ('cent', 'Cent'),
    ('ground', 'Ground'),
    ('acre', 'Acre'),
    ('hectare', 'Hectare'),
]

DOCUMENT_TYPE_CHOICES = [
    ('patta', 'Patta'),
    ('chitta', 'Chitta'),
    ('ec', 'Encumbrance Certificate'),
    ('sale_deed', 'Sale Deed'),
    ('title_deed', 'Title Deed'),
    ('survey_sketch', 'Survey Sketch'),
    ('rera', 'RERA Registration'),
]


class Property(TimestampedModel):
    """
    Main Property model with Indian land-specific fields
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_properties')
    broker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='brokered_properties',
        limit_choices_to={'role__in': ['broker']}
    )

    # Basic Information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Pricing
    price = models.DecimalField(max_digits=15, decimal_places=2)
    is_negotiable = models.BooleanField(default=True)
    price_per_unit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Auto-calculated price per sqft"
    )

    # Indian Land-Specific Fields
    total_area = models.DecimalField(max_digits=10, decimal_places=2)
    area_unit = models.CharField(max_length=20, choices=AREA_UNIT_CHOICES)
    survey_number = models.CharField(max_length=50, blank=True, null=True)
    patta_number = models.CharField(max_length=50, blank=True, null=True)
    chitta_number = models.CharField(max_length=50, blank=True, null=True)
    rera_number = models.CharField(max_length=100, blank=True, null=True, help_text="RERA registration number")

    # Location Information
    location = models.PointField(srid=4326)  # GPS coordinates
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10)

    # Features and Amenities (JSON for flexibility)
    amenities = models.JSONField(default=dict, blank=True)
    features = models.JSONField(default=dict, blank=True)

    # Contact Information (shown to interested buyers)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)

    # Verification and Approval
    verification_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_properties'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    # Analytics
    view_count = models.IntegerField(default=0)
    save_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'properties'
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        indexes = [
            models.Index(fields=['city', 'property_type']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['price']),
            models.Index(fields=['owner']),
        ]

    def __str__(self):
        return f"{self.title} - {self.city}"

    def save(self, *args, **kwargs):
        # Calculate price per unit
        if self.total_area and self.price:
            # Convert area to sqft for consistency
            area_in_sqft = self._convert_to_sqft(self.total_area, self.area_unit)
            self.price_per_unit = self.price / area_in_sqft if area_in_sqft > 0 else None

        super().save(*args, **kwargs)

    @staticmethod
    def _convert_to_sqft(area, unit):
        """Convert any area unit to square feet"""
        conversions = {
            'sqft': 1,
            'cent': 435.6,
            'ground': 2400,
            'acre': 43560,
            'hectare': 107639,
        }
        return area * conversions.get(unit, 1)

    def increment_view_count(self):
        """Increment property view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def increment_save_count(self):
        """Increment property save count"""
        self.save_count += 1
        self.save(update_fields=['save_count'])


class PropertyImage(BaseModel):
    """
    Property images/gallery
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    image_hash = models.CharField(max_length=64, blank=True, null=True, help_text="For duplicate detection")
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'property_images'
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'
        ordering = ['sort_order']

    def __str__(self):
        return f"Image for {self.property.title}"


class PropertyDocument(BaseModel):
    """
    Legal documents (Patta, Chitta, EC, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file_url = models.URLField()
    original_filename = models.CharField(max_length=255)
    extracted_data = models.JSONField(default=dict, blank=True, help_text="OCR extracted data")
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'property_documents'
        verbose_name = 'Property Document'
        verbose_name_plural = 'Property Documents'

    def __str__(self):
        return f"{self.get_document_type_display()} for {self.property.title}"


class Wishlist(BaseModel):
    """
    Buyer's saved/favorited properties
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='saved_by')

    class Meta:
        db_table = 'wishlist'
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlist'
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user.email} saved {self.property.title}"


class Review(BaseModel):
    """
    Property and vendor reviews
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    is_verified_transaction = models.BooleanField(default=False)

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ('property', 'buyer')

    def __str__(self):
        return f"Review by {self.buyer.email} for {self.property.title}"