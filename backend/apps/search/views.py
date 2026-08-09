"""
Search API views - Elasticsearch integration
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.core.paginator import Paginator

from .serializers import (
    SearchFiltersSerializer,
    PropertySearchSerializer,
    LocationAutocompleteSerializer,
    PropertyAggregationSerializer,
)
from .filters import PropertySearchBuilder


@api_view(['GET'])
@permission_classes([AllowAny])
def search_properties(request):
    """
    Search properties with advanced filters and geolocation
    
    Query Parameters:
    - q: Text search query
    - city: City name
    - state: State name
    - latitude: User latitude
    - longitude: User longitude
    - radius_km: Search radius (default: 10)
    - property_type: Property type (comma-separated)
    - purpose: sale/rent/lease (comma-separated)
    - min_price: Minimum price
    - max_price: Maximum price
    - min_area: Minimum area
    - max_area: Maximum area
    - sort_by: relevance, price_low, price_high, newest, popular
    - page: Page number (default: 1)
    - page_size: Results per page (default: 20, max: 100)
    """
    
    # Parse and validate filters
    filters_serializer = SearchFiltersSerializer(data=request.query_params)
    if not filters_serializer.is_valid():
        return Response(filters_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    filters = filters_serializer.validated_data
    
    # Generate cache key
    cache_key = f"search:{str(filters)}"
    cached_results = cache.get(cache_key)
    
    if cached_results:
        return Response(cached_results)
    
    try:
        # Build Elasticsearch query
        builder = PropertySearchBuilder()
        search_query = builder.build_query(filters)
        
        # Get total count before pagination
        total_count = search_query.count()
        
        # Apply pagination
        page = filters.get('page', 1)
        page_size = filters.get('page_size', 20)
        start = (page - 1) * page_size
        end = start + page_size
        
        search_query = search_query[start:end]
        results = search_query.execute()
        
        # Serialize results
        properties = []
        for hit in results:
            try:
                prop_data = hit.to_dict()
                properties.append(prop_data)
            except Exception as e:
                print(f"Error serializing property: {e}")
                continue
        
        # Get aggregations for faceted search
        agg_search = builder.build_query(filters)
        agg_search = builder.get_aggregations(agg_search)
        agg_results = agg_search.execute()
        
        aggregations = {
            'property_types': {
                bucket.key: bucket.doc_count 
                for bucket in agg_results.aggregations.property_types.buckets
            },
            'purposes': {
                bucket.key: bucket.doc_count 
                for bucket in agg_results.aggregations.purposes.buckets
            },
            'cities': {
                bucket.key: bucket.doc_count 
                for bucket in agg_results.aggregations.cities.buckets
            },
            'amenities': {
                bucket.key: bucket.doc_count 
                for bucket in agg_results.aggregations.amenities.buckets
            },
        }
        
        # Calculate pagination
        total_pages = (total_count + page_size - 1) // page_size
        
        response_data = {
            'count': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'page_size': page_size,
            'results': properties,
            'aggregations': aggregations,
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, response_data, 300)
        
        return Response(response_data)
    
    except Exception as e:
        return Response(
            {'error': f'Search failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def search_nearby_properties(request):
    """
    Find properties near user's location
    
    Query Parameters:
    - latitude: User latitude (required)
    - longitude: User longitude (required)
    - radius_km: Search radius in kilometers (default: 10, max: 100)
    - limit: Number of results (default: 20, max: 100)
    """
    
    latitude = request.query_params.get('latitude')
    longitude = request.query_params.get('longitude')
    radius_km = float(request.query_params.get('radius_km', 10))
    limit = int(request.query_params.get('limit', 20))
    
    if not latitude or not longitude:
        return Response(
            {'error': 'latitude and longitude are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return Response(
            {'error': 'Invalid latitude or longitude'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if radius_km <= 0 or radius_km > 100:
        return Response(
            {'error': 'radius_km must be between 0 and 100'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if limit <= 0 or limit > 100:
        return Response(
            {'error': 'limit must be between 1 and 100'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        builder = PropertySearchBuilder()
        results = builder.search_nearby_properties(latitude, longitude, radius_km, limit)
        
        properties = [hit.to_dict() for hit in results]
        
        return Response({
            'count': len(properties),
            'latitude': latitude,
            'longitude': longitude,
            'radius_km': radius_km,
            'results': properties,
        })
    
    except Exception as e:
        return Response(
            {'error': f'Nearby search failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def location_autocomplete(request):
    """
    Autocomplete for location search
    
    Query Parameters:
    - q: Search query (required, min 2 characters)
    - size: Number of suggestions (default: 10, max: 50)
    """
    
    query = request.query_params.get('q', '').strip()
    size = int(request.query_params.get('size', 10))
    
    if len(query) < 2:
        return Response(
            {'error': 'Query must be at least 2 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if size > 50:
        size = 50
    
    # Check cache first
    cache_key = f"autocomplete:{query}:{size}"
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)
    
    try:
        builder = PropertySearchBuilder()
        suggestions = builder.autocomplete_location(query, size)
        
        response_data = {
            'query': query,
            'suggestions': suggestions,
        }
        
        # Cache for 1 hour
        cache.set(cache_key, response_data, 3600)
        
        return Response(response_data)
    
    except Exception as e:
        return Response(
            {'error': f'Autocomplete failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def search_by_survey_number(request):
    """
    Search for properties by Indian survey number
    
    Query Parameters:
    - survey_number: Survey number (required)
    """
    
    survey_number = request.query_params.get('survey_number', '').strip()
    
    if not survey_number:
        return Response(
            {'error': 'survey_number is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        builder = PropertySearchBuilder()
        results = builder.search_by_survey_number(survey_number)
        
        properties = [hit.to_dict() for hit in results]
        
        return Response({
            'survey_number': survey_number,
            'count': len(properties),
            'results': properties,
        })
    
    except Exception as e:
        return Response(
            {'error': f'Survey search failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )