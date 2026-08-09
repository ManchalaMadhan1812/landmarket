"""
Property serializers for API endpoints
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Property, PropertyImage, PropertyDocument,
    Wishlist, Review
)

User = get_user_model()


class PropertyImageSerializer(serializers.ModelSerializer):
    """Serializer for property images"""
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'image_url', 'is_primary', 'sort_order', 'created_at']
        read_only_fields = ['id', 'created_at']


class PropertyDocumentSerializer(serializers.ModelSerializer):
    """Serializer for property documents"""
    
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = PropertyDocument
        fields = [
            'id', 'document_type', 'document_type_display', 'file_url',
            'original_filename', 'extracted_data', 'is_verified', 'verified_at'
        ]
        read_only_fields = ['id', 'created_at']


class PropertyListSerializer(serializers.ModelSerializer):
    """
    Serializer for property listing (simplified)
    """
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'property_type', 'purpose', 'price',
            'total_area', 'area_unit', 'city', 'state', 'pincode',
            'owner_name', 'status', 'view_count', 'save_count',
            'primary_image', 'images', 'verification_score', 'created_at'
        ]
        read_only_fields = ['id', 'view_count', 'save_count', 'created_at']

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return PropertyImageSerializer(primary_image).data
        # Return first image if no primary set
        first_image = obj.images.first()
        if first_image:
            return PropertyImageSerializer(first_image).data
        return None


class PropertyDetailSerializer(serializers.ModelSerializer):
    """
    Detailed property serializer (full details)
    """
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    broker_name = serializers.CharField(source='broker.get_full_name', read_only=True, allow_null=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    documents = PropertyDocumentSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'property_type', 'purpose',
            'price', 'is_negotiable', 'price_per_unit', 'total_area', 'area_unit',
            'survey_number', 'patta_number', 'chitta_number', 'rera_number',
            'address', 'city', 'state', 'district', 'pincode',
            'latitude', 'longitude', 'amenities', 'features',
            'owner_name', 'broker_name', 'contact_name', 'contact_phone',
            'status', 'verification_score', 'view_count', 'save_count',
            'images', 'documents', 'reviews', 'is_saved',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'view_count', 'save_count', 'verification_score',
            'price_per_unit', 'created_at', 'updated_at'
        ]

    def get_reviews(self, obj):
        reviews = obj.reviews.all()[:5]  # Latest 5 reviews
        return ReviewSerializer(reviews, many=True).data

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(
                user=request.user,
                property=obj
            ).exists()
        return False

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None


class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating properties"""
    
    images = PropertyImageSerializer(many=True, read_only=True)
    documents = PropertyDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'property_type', 'purpose',
            'price', 'is_negotiable', 'total_area', 'area_unit',
            'survey_number', 'patta_number', 'chitta_number', 'rera_number',
            'address', 'city', 'state', 'district', 'pincode',
            'amenities', 'features', 'contact_name', 'contact_phone',
            'images', 'documents'
        ]

    def validate(self, attrs):
        # Validate location coordinates if provided
        if 'latitude' in self.context and 'longitude' in self.context:
            attrs['location'] = Point(
                self.context['longitude'],
                self.context['latitude'],
                srid=4326
            )
        return attrs


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlist"""
    
    property = PropertyListSerializer(read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'property', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews"""
    
    buyer_name = serializers.CharField(source='buyer.get_full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'buyer_name', 'rating', 'comment',
            'is_verified_transaction', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PropertyApprovalSerializer(serializers.Serializer):
    """Serializer for property approval/rejection"""
    
    approved = serializers.BooleanField()
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs['approved'] and not attrs.get('rejection_reason'):
            raise serializers.ValidationError(
                "Rejection reason is required when rejecting a property"
            )
        return attrs