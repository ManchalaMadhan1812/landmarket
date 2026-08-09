"""
Elasticsearch query builders and filters for property search
"""

from elasticsearch_dsl import Q, Search, A
from elasticsearch import Elasticsearch
from django.conf import settings


class PropertySearchBuilder:
    """
    Helper class to build Elasticsearch queries for property search
    """

    def __init__(self):
        self.es_client = Elasticsearch([settings.ELASTICSEARCH_DSL['default']['hosts']])

    def build_query(self, filters):
        """
        Build Elasticsearch query from filter parameters
        
        Args:
            filters (dict): Filter parameters from SearchFiltersSerializer
            
        Returns:
            Search: Elasticsearch Search object
        """
        search = Search(using=self.es_client, index='properties')
        
        # Start with must-have filters
        must_queries = []
        should_queries = []
        
        # 1. Text search (if provided)
        if filters.get('q'):
            query_text = filters['q']
            should_queries.extend([
                Q('match', title={'query': query_text, 'fuzziness': 'AUTO', 'boost': 3}),
                Q('match', description=query_text),
                Q('match', address=query_text),
                Q('match', survey_number=query_text),
            ])
        
        # 2. Location-based search
        if filters.get('latitude') and filters.get('longitude'):
            radius = filters.get('radius_km', 10)
            must_queries.append(
                Q('geo_distance', 
                  distance=f'{radius}km',
                  location={
                      'lat': filters['latitude'],
                      'lon': filters['longitude']
                  })
            )
        elif filters.get('city'):
            # City-based search if no coordinates
            must_queries.append(Q('term', city=filters['city'].lower()))
        
        if filters.get('state'):
            must_queries.append(Q('term', state=filters['state'].lower()))
        
        # 3. Property type filter
        if filters.get('property_type'):
            must_queries.append(
                Q('terms', property_type=filters['property_type'])
            )
        
        # 4. Purpose filter
        if filters.get('purpose'):
            must_queries.append(
                Q('terms', purpose=filters['purpose'])
            )
        
        # 5. Price range filter
        price_query = Q('range', price={})
        if filters.get('min_price'):
            price_query.to_dict()['range']['price']['gte'] = filters['min_price']
        if filters.get('max_price'):
            price_query.to_dict()['range']['price']['lte'] = filters['max_price']
        if filters.get('min_price') or filters.get('max_price'):
            must_queries.append(price_query)
        
        # 6. Area range filter
        area_query = Q('range', total_area={})
        if filters.get('min_area'):
            area_query.to_dict()['range']['total_area']['gte'] = filters['min_area']
        if filters.get('max_area'):
            area_query.to_dict()['range']['total_area']['lte'] = filters['max_area']
        if filters.get('min_area') or filters.get('max_area'):
            must_queries.append(area_query)
        
        # 7. Status filter (always active for public search)
        must_queries.append(Q('term', status='active'))
        
        # 8. Amenities filter
        if filters.get('amenities'):
            amenities_queries = [Q('match', amenities=amenity) for amenity in filters['amenities']]
            must_queries.append(Q('bool', should=amenities_queries))
        
        # Combine queries
        if must_queries:
            search = search.query('bool', must=must_queries)
        
        if should_queries:
            search = search.query('bool', should=should_queries, minimum_should_match=1)
        
        # Apply sorting
        sort_by = filters.get('sort_by', 'relevance')
        if sort_by == 'price_low':
            search = search.sort('price')
        elif sort_by == 'price_high':
            search = search.sort('-price')
        elif sort_by == 'newest':
            search = search.sort('-created_at')
        elif sort_by == 'popular':
            search = search.sort('-view_count', '-save_count')
        # 'relevance' is default Elasticsearch sorting
        
        return search

    def get_aggregations(self, search_query):
        """
        Get faceted aggregations for filters
        
        Args:
            search_query (Search): Elasticsearch Search object
            
        Returns:
            dict: Aggregation results
        """
        search = search_query
        
        # Add aggregations for faceted search
        search.aggs.bucket('property_types', 'terms', field='property_type', size=10)
        search.aggs.bucket('purposes', 'terms', field='purpose', size=10)
        search.aggs.bucket('cities', 'terms', field='city', size=20)
        search.aggs.bucket('price_ranges', 'histogram', field='price', interval=100000)
        search.aggs.bucket('amenities', 'terms', field='amenities', size=20)
        
        return search

    def search_nearby_properties(self, latitude, longitude, radius_km=10, limit=20):
        """
        Find properties near a location
        
        Args:
            latitude (float): User latitude
            longitude (float): User longitude
            radius_km (float): Search radius in kilometers
            limit (int): Number of results to return
            
        Returns:
            list: List of properties with distance
        """
        search = Search(using=self.es_client, index='properties')
        search = search.query('bool', must=[
            Q('geo_distance',
              distance=f'{radius_km}km',
              location={'lat': latitude, 'lon': longitude}),
            Q('term', status='active')
        ])
        
        # Sort by distance
        search = search.extra(
            sort=['_geo_distance:location'],
            sort_args={
                'location': {
                    'lat': latitude,
                    'lon': longitude,
                    'unit': 'km'
                }
            }
        )
        
        search = search[0:limit]
        return search.execute()

    def autocomplete_location(self, query, size=10):
        """
        Autocomplete location search
        
        Args:
            query (str): Partial location query
            size (int): Number of suggestions
            
        Returns:
            list: List of location suggestions
        """
        search = Search(using=self.es_client, index='properties')
        
        search = search.query('multi_match', query=query, fields=[
            'city.autocomplete',
            'state.autocomplete',
            'address.autocomplete'
        ])
        
        # Aggregate unique cities and states
        search.aggs.bucket('cities', 'terms', field='city', size=size)
        search.aggs.bucket('states', 'terms', field='state', size=size)
        
        results = search.execute()
        
        suggestions = []
        for bucket in results.aggregations.cities.buckets:
            suggestions.append({
                'label': bucket.key,
                'value': bucket.key,
                'type': 'city'
            })
        
        for bucket in results.aggregations.states.buckets:
            suggestions.append({
                'label': bucket.key,
                'value': bucket.key,
                'type': 'state'
            })
        
        return suggestions[:size]

    def search_by_survey_number(self, survey_number):
        """
        Search for properties by survey number (Indian land records)
        
        Args:
            survey_number (str): Survey number to search
            
        Returns:
            Search results
        """
        search = Search(using=self.es_client, index='properties')
        search = search.query('term', survey_number=survey_number)
        return search.execute()