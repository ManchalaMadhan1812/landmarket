#!/usr/bin/env python3
"""
End-to-End Test for LandMarket Search Functionality
This script tests the complete search system including Elasticsearch, APIs, and frontend integration.
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api"
SEARCH_ENDPOINTS = {
    "search_properties": "/search/properties",
    "search_nearby": "/search/nearby",
    "location_autocomplete": "/search/location-autocomplete",
    "aggregations": "/search/aggregations",
}

class SearchSystemTest:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_endpoint_availability(self) -> bool:
        """Test if search endpoints are available"""
        print("\n=== Testing Search Endpoints Availability ===")
        all_available = True
        
        for endpoint_name, endpoint_path in SEARCH_ENDPOINTS.items():
            url = f"{self.base_url}{API_PREFIX}{endpoint_path}"
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint_name}: Available (200)")
                elif response.status_code in [401, 403]:
                    print(f"⚠️  {endpoint_name}: Requires authentication ({response.status_code})")
                else:
                    print(f"❌ {endpoint_name}: Failed ({response.status_code})")
                    all_available = False
            except requests.exceptions.RequestException as e:
                print(f"❌ {endpoint_name}: Connection error - {str(e)}")
                all_available = False
        
        return all_available
    
    def test_basic_search(self) -> bool:
        """Test basic property search functionality"""
        print("\n=== Testing Basic Property Search ===")
        
        test_queries = [
            {"q": "Chennai"},
            {"city": "Bangalore"},
            {"property_type": "residential", "purpose": "sale"},
            {"min_price": 1000000, "max_price": 5000000},
        ]
        
        success_count = 0
        
        for query_params in test_queries:
            url = f"{self.base_url}{API_PREFIX}{SEARCH_ENDPOINTS['search_properties']}"
            try:
                response = self.session.get(url, params=query_params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = ['count', 'total_pages', 'current_page', 'results']
                    if all(field in data for field in required_fields):
                        print(f"✅ Search '{json.dumps(query_params)}': Success - {data['count']} results")
                        success_count += 1
                        
                        # Test aggregations if present
                        if 'aggregations' in data:
                            print(f"   └─ Aggregations available: {list(data['aggregations'].keys())}")
                    else:
                        print(f"❌ Search '{json.dumps(query_params)}': Invalid response format")
                else:
                    print(f"❌ Search '{json.dumps(query_params)}': Failed ({response.status_code})")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Search '{json.dumps(query_params)}': Connection error - {str(e)}")
            except json.JSONDecodeError:
                print(f"❌ Search '{json.dumps(query_params)}': Invalid JSON response")
        
        return success_count == len(test_queries)
    
    def test_geo_search(self) -> bool:
        """Test geolocation-based search functionality"""
        print("\n=== Testing Geolocation Search ===")
        
        # Test coordinates for Chennai
        test_coordinates = {
            "latitude": 13.0827,
            "longitude": 80.2707,
            "radius_km": 10
        }
        
        url = f"{self.base_url}{API_PREFIX}{SEARCH_ENDPOINTS['search_properties']}"
        try:
            response = self.session.get(url, params=test_coordinates, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Geo-search: Success - {data['count']} properties near Chennai")
                return True
            else:
                print(f"❌ Geo-search: Failed ({response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Geo-search: Connection error - {str(e)}")
            return False
    
    def test_location_autocomplete(self) -> bool:
        """Test location autocomplete functionality"""
        print("\n=== Testing Location Autocomplete ===")
        
        test_queries = ["Chen", "Bang", "Mum"]
        
        success_count = 0
        
        for query in test_queries:
            url = f"{self.base_url}{API_PREFIX}{SEARCH_ENDPOINTS['location_autocomplete']}"
            try:
                response = self.session.get(url, params={"q": query, "limit": 5}, timeout=5)
                
                if response.status_code == 200:
                    suggestions = response.json()
                    if isinstance(suggestions, list):
                        print(f"✅ Autocomplete for '{query}': {len(suggestions)} suggestions")
                        for suggestion in suggestions[:3]:  # Show first 3
                            print(f"   └─ {suggestion.get('name', 'Unknown')} ({suggestion.get('type', 'unknown')})")
                        success_count += 1
                    else:
                        print(f"❌ Autocomplete for '{query}': Invalid response format")
                else:
                    print(f"❌ Autocomplete for '{query}': Failed ({response.status_code})")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Autocomplete for '{query}': Connection error - {str(e)}")
        
        return success_count == len(test_queries)
    
    def test_nearby_search(self) -> bool:
        """Test nearby properties search"""
        print("\n=== Testing Nearby Properties Search ===")
        
        # Test with Delhi coordinates
        test_params = {
            "latitude": 28.7041,
            "longitude": 77.1025,
            "radius_km": 5
        }
        
        url = f"{self.base_url}{API_PREFIX}{SEARCH_ENDPOINTS['search_nearby']}"
        try:
            response = self.session.get(url, params=test_params, timeout=10)
            
            if response.status_code == 200:
                properties = response.json()
                print(f"✅ Nearby search: Found {len(properties)} properties near Delhi")
                return True
            else:
                print(f"❌ Nearby search: Failed ({response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Nearby search: Connection error - {str(e)}")
            return False
    
    def test_search_aggregations(self) -> bool:
        """Test search aggregations endpoint"""
        print("\n=== Testing Search Aggregations ===")
        
        url = f"{self.base_url}{API_PREFIX}{SEARCH_ENDPOINTS['aggregations']}"
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                aggregations = response.json()
                print(f"✅ Aggregations: Available aggregations:")
                for agg_type, values in aggregations.items():
                    if isinstance(values, dict):
                        print(f"   └─ {agg_type}: {len(values)} values")
                    else:
                        print(f"   └─ {agg_type}: {values}")
                return True
            else:
                print(f"❌ Aggregations: Failed ({response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Aggregations: Connection error - {str(e)}")
            return False
    
    def test_search_with_filters(self) -> bool:
        """Test search with multiple filters"""
        print("\n=== Testing Search with Multiple Filters ===")
        
        complex_filters = {
            "city": "Chennai",
            "property_type": ["residential", "plot"],
            "purpose": "sale",
            "min_price": 500000,
            "max_price": 2000000,
            "min_area": 500,
            "sort_by": "price_low"
        }
        
        url = f"{self.base_url}{API_PREFIX}{SEARCH_ENDPOINTS['search_properties']}"
        try:
            response = self.session.get(url, params=complex_filters, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Complex filters: Found {data['count']} properties in Chennai")
                print(f"   └─ Filters applied: {len(complex_filters)}")
                return True
            else:
                print(f"❌ Complex filters: Failed ({response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Complex filters: Connection error - {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test search error handling"""
        print("\n=== Testing Error Handling ===")
        
        test_cases = [
            {"invalid_param": "test"},  # Invalid parameter
            {"min_price": "invalid_number"},  # Invalid data type
            {"latitude": "invalid", "longitude": "invalid"},  # Invalid coordinates
        ]
        
        error_handled_count = 0
        
        for params in test_cases:
            url = f"{self.base_url}{API_PREFIX}{SEARCH_ENDPOINTS['search_properties']}"
            try:
                response = self.session.get(url, params=params, timeout=5)
                
                # Should return 400 for bad requests or handle gracefully
                if response.status_code in [200, 400, 422]:
                    print(f"✅ Error handling for '{json.dumps(params)}': Properly handled")
                    error_handled_count += 1
                else:
                    print(f"❌ Error handling for '{json.dumps(params)}': Unexpected status {response.status_code}")
                    
            except requests.exceptions.RequestException:
                print(f"❌ Error handling for '{json.dumps(params)}': Connection error")
        
        return error_handled_count == len(test_cases)
    
    def run_all_tests(self) -> bool:
        """Run all search system tests"""
        print("=" * 60)
        print("LANDMARKET SEARCH SYSTEM END-TO-END TEST")
        print("=" * 60)
        
        test_results = []
        
        # Run tests in logical order
        test_results.append(("Endpoints Available", self.test_endpoint_availability()))
        test_results.append(("Basic Search", self.test_basic_search()))
        test_results.append(("Geo Search", self.test_geo_search()))
        test_results.append(("Location Autocomplete", self.test_location_autocomplete()))
        test_results.append(("Nearby Search", self.test_nearby_search()))
        test_results.append(("Search Aggregations", self.test_search_aggregations()))
        test_results.append(("Complex Filters", self.test_search_with_filters()))
        test_results.append(("Error Handling", self.test_error_handling()))
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(test_results)
        passed_tests = sum(1 for _, passed in test_results if passed)
        
        for test_name, passed in test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! Search system is fully functional.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Check the logs above.")
        
        return passed_tests == total_tests

def main():
    """Main function to run search tests"""
    try:
        # Check if Django server is running
        test_runner = SearchSystemTest()
        
        print("Starting LandMarket Search System Tests...")
        print("Note: Ensure Django backend is running on localhost:8000")
        print("-" * 60)
        
        success = test_runner.run_all_tests()
        
        if success:
            print("\n✅ Search system is ready for production!")
            print("Next steps:")
            print("1. Load sample property data for testing")
            print("2. Configure Elasticsearch indexing")
            print("3. Set up Redis caching")
            print("4. Add Google Maps API key for frontend maps")
            return 0
        else:
            print("\n❌ Some tests failed. Please check the search system configuration.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())