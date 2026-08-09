"""
Search serializers for Elasticsearch results
"""

from rest_framework import serializers


class PropertySearchSerializer(serializers.Serializer):
    """
    Serializer for Elasticsearch property search results
    """
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    property_type = serializers.CharField()
    purpose = serializers.CharField()
    price = serializers.IntegerField()
    total_area = serializers.FloatField()
    area_unit = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    address = serializers.CharField()
    location = serializers.DictField()
    
    owner_name = serializers.CharField()
    owner_email = serializers.CharField()
    
    status = serializers.CharField()
    verification_score = serializers.IntegerField()
    view_count = serializers.IntegerField()
    save_count = serializers.IntegerField()
    avg_rating = serializers.FloatField()
    review_count = serializers.IntegerField()
    
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    
    survey_number = serializers.CharField(required=False, allow_blank=True)
    patta_number = serializers.CharField(required=False, allow_blank=True)


class SearchFiltersSerializer(serializers.Serializer):
    """
    Serializer for search filter parameters
    """
    # Text search
    q = serializers.CharField(required=False, allow_blank=True)
    
    # Location based
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    radius_km = serializers.FloatField(required=False, default=10)
    city = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    
    # Property filters
    property_type = serializers.MultipleChoiceField(
        choices=[
            'residential', 'commercial', 'agricultural',
            'industrial', 'plot', 'apartment', 'house'
        ],
        required=False
    )
    purpose = serializers.MultipleChoiceField(
        choices=['sale', 'rent', 'lease'],
        required=False
    )
    
    # Price filters
    min_price = serializers.IntegerField(required=False)
    max_price = serializers.IntegerField(required=False)
    
    # Area filters
    min_area = serializers.FloatField(required=False)
    max_area = serializers.FloatField(required=False)
    
    # Amenities filter
    amenities = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    
    # Sorting and pagination
    sort_by = serializers.ChoiceField(
        choices=['relevance', 'price_low', 'price_high', 'newest', 'popular'],
        required=False,
        default='relevance'
    )
    page = serializers.IntegerField(required=False, default=1, min_value=1)
    page_size = serializers.IntegerField(required=False, default=20, min_value=1, max_value=100)
    
    def validate(self, attrs):
        """Validate filter combinations"""
        # Validate price range
        min_price = attrs.get('min_price')
        max_price = attrs.get('max_price')
        if min_price and max_price and min_price > max_price:
            raise serializers.ValidationError("min_price cannot be greater than max_price")
        
        # Validate area range
        min_area = attrs.get('min_area')
        max_area = attrs.get('max_area')
        if min_area and max_area and min_area > max_area:
            raise serializers.ValidationError("min_area cannot be greater than max_area")
        
        # Validate radius
        radius = attrs.get('radius_km')
        if radius and radius <= 0:
            raise serializers.ValidationError("radius_km must be greater than 0")
        if radius and radius > 100:
            raise serializers.ValidationError("radius_km cannot exceed 100 km")
        
        return attrs


class PropertyAggregationSerializer(serializers.Serializer):
    """
    Serializer for search aggregations (facets)
    """
    property_types = serializers.DictField()
    purposes = serializers.DictField()
    cities = serializers.DictField()
    price_ranges = serializers.DictField()
    amenities = serializers.DictField()


class LocationAutocompleteSerializer(serializers.Serializer):
    """
    Serializer for location autocomplete results
    """
    label = serializers.CharField()  # Display text
    value = serializers.CharField()  # Value to use
    city = serializers.CharField()
    state = serializers.CharField()
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)