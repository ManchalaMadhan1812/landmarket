"""
Admin configuration for property models
"""

from django.contrib import admin
from .models import Property, PropertyImage, PropertyDocument, Wishlist, Review


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Property admin"""
    list_display = (
        'title', 'property_type', 'city', 'price', 'status',
        'owner', 'verification_score', 'view_count', 'created_at'
    )
    list_filter = (
        'property_type', 'purpose', 'status', 'city', 'state', 'created_at'
    )
    search_fields = ('title', 'description', 'address', 'city', 'survey_number')
    readonly_fields = (
        'id', 'price_per_unit', 'view_count', 'save_count',
        'created_at', 'updated_at'
    )
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'property_type', 'purpose')
        }),
        ('Pricing & Area', {
            'fields': (
                'price', 'is_negotiable', 'price_per_unit',
                'total_area', 'area_unit'
            )
        }),
        ('Land Records (India)', {
            'fields': (
                'survey_number', 'patta_number', 'chitta_number', 'rera_number'
            ),
            'classes': ('collapse',)
        }),
        ('Location', {
            'fields': (
                'location', 'address', 'city', 'state', 'district', 'pincode'
            )
        }),
        ('Features & Amenities', {
            'fields': ('amenities', 'features')
        }),
        ('Contact', {
            'fields': ('contact_name', 'contact_phone'),
            'classes': ('collapse',)
        }),
        ('Owner & Broker', {
            'fields': ('owner', 'broker')
        }),
        ('Verification', {
            'fields': (
                'verification_score', 'status',
                'approved_by', 'approved_at', 'rejection_reason'
            )
        }),
        ('Analytics', {
            'fields': ('view_count', 'save_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_properties', 'reject_properties']

    def approve_properties(self, request, queryset):
        updated = queryset.update(status='active', approved_by=request.user)
        self.message_user(request, f'{updated} properties approved.')

    def reject_properties(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} properties rejected.')


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    """Property Image admin"""
    list_display = ('property', 'is_primary', 'sort_order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('property__title',)
    readonly_fields = ('id', 'image_hash', 'created_at', 'updated_at')


@admin.register(PropertyDocument)
class PropertyDocumentAdmin(admin.ModelAdmin):
    """Property Document admin"""
    list_display = (
        'property', 'document_type', 'is_verified', 'verified_at'
    )
    list_filter = ('document_type', 'is_verified', 'created_at')
    search_fields = ('property__title', 'original_filename')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Wishlist admin"""
    list_display = ('user', 'property', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'property__title')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Review admin"""
    list_display = (
        'property', 'buyer', 'rating', 'is_verified_transaction', 'created_at'
    )
    list_filter = ('rating', 'is_verified_transaction', 'created_at')
    search_fields = ('property__title', 'buyer__email', 'comment')
    readonly_fields = ('id', 'created_at', 'updated_at')