import React, { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useQuery } from '@tanstack/react-query'
import { MapContainer, SearchFilters, PropertyCard, SearchHeader } from '../components/search'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import { useLocationStore } from '../stores/locationStore'
import { searchProperties } from '../services/searchService'

const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const { selectedLocation } = useLocationStore()
  
  // Search state
  const [showMap, setShowMap] = useState(true)
  const [filters, setFilters] = useState(() => {
    const initialFilters: any = {
      q: searchParams.get('q') || '',
      city: searchParams.get('city') || '',
      property_type: searchParams.getAll('property_type') || [],
      purpose: searchParams.getAll('purpose') || [],
      min_price: searchParams.get('min_price') || '',
      max_price: searchParams.get('max_price') || '',
      min_area: searchParams.get('min_area') || '',
      max_area: searchParams.get('max_area') || '',
      sort_by: searchParams.get('sort_by') || 'relevance',
      page: parseInt(searchParams.get('page') || '1'),
      page_size: parseInt(searchParams.get('page_size') || '20'),
    }

    // Add location if available
    if (selectedLocation) {
      initialFilters.latitude = selectedLocation.latitude
      initialFilters.longitude = selectedLocation.longitude
      initialFilters.radius_km = 10
    }

    return initialFilters
  })

  // Fetch properties
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['search', filters],
    queryFn: () => searchProperties(filters),
    enabled: false, // Don't auto-fetch on component mount
  })

  // Trigger search on filter change
  useEffect(() => {
    // Update URL with search params
    const params = new URLSearchParams()
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(key, v))
        } else {
          params.set(key, value.toString())
        }
      }
    })

    setSearchParams(params)
    refetch()
  }, [filters, setSearchParams, refetch])

  // Initial search on mount
  useEffect(() => {
    refetch()
  }, [refetch])

  const handleSearch = (newFilters: any) => {
    setFilters({ ...filters, ...newFilters, page: 1 })
  }

  const handlePageChange = (page: number) => {
    setFilters({ ...filters, page })
  }

  const handleClearFilters = () => {
    setFilters({
      q: '',
      city: '',
      property_type: [],
      purpose: [],
      min_price: '',
      max_price: '',
      min_area: '',
      max_area: '',
      sort_by: 'relevance',
      page: 1,
      page_size: 20,
    })
  }

  const handleLocationSelect = (location: { latitude: number; longitude: number; city?: string }) => {
    setFilters({
      ...filters,
      latitude: location.latitude,
      longitude: location.longitude,
      city: location.city || '',
      page: 1,
    })
  }

  return (
    <>
      <Helmet>
        <title>Search Properties - LandMarket</title>
        <meta name="description" content="Find properties across India with advanced search filters, maps, and location-based discovery." />
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        {/* Search Header */}
        <SearchHeader
          searchQuery={filters.q}
          onSearchChange={(q) => handleSearch({ q })}
          onLocationSelect={handleLocationSelect}
          selectedLocation={selectedLocation}
        />

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col lg:flex-row gap-6">
            {/* Filters Sidebar - 25% width */}
            <div className="lg:w-1/4">
              <SearchFilters
                filters={filters}
                aggregations={data?.aggregations}
                onFilterChange={handleSearch}
                onClearFilters={handleClearFilters}
              />
            </div>

            {/* Results Area - 75% width */}
            <div className="lg:w-3/4">
              {/* Toggle Map/List View */}
              <div className="mb-6 flex justify-between items-center">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">
                    {data?.count || 0} Properties Found
                  </h2>
                  {selectedLocation && (
                    <p className="text-sm text-gray-600">
                      Searching near {selectedLocation.city || 'your location'}
                    </p>
                  )}
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600 hidden md:inline">View:</span>
                  <button
                    onClick={() => setShowMap(false)}
                    className={`px-3 py-1 text-sm rounded-md ${!showMap ? 'bg-primary-100 text-primary-700' : 'text-gray-600 hover:bg-gray-100'}`}
                  >
                    List
                  </button>
                  <button
                    onClick={() => setShowMap(true)}
                    className={`px-3 py-1 text-sm rounded-md ${showMap ? 'bg-primary-100 text-primary-700' : 'text-gray-600 hover:bg-gray-100'}`}
                  >
                    Map
                  </button>
                </div>
              </div>

              {/* Error State */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                  <p className="text-red-700">Error loading properties. Please try again.</p>
                </div>
              )}

              {/* Loading State */}
              {isLoading && (
                <div className="flex justify-center items-center h-64">
                  <LoadingSpinner size="lg" />
                </div>
              )}

              {/* Results */}
              {!isLoading && data && (
                <>
                  {showMap ? (
                    // Map View
                    <div className="h-[600px] rounded-lg overflow-hidden border border-gray-200">
                      <MapContainer
                        properties={data.results}
                        center={{
                          lat: filters.latitude || 20.5937,
                          lng: filters.longitude || 78.9629
                        }}
                        zoom={filters.city ? 12 : 6}
                      />
                    </div>
                  ) : (
                    // List View
                    <>
                      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                        {data.results.map((property) => (
                          <PropertyCard
                            key={property.id}
                            property={property}
                            onSave={() => {}}
                          />
                        ))}
                      </div>

                      {/* No Results */}
                      {data.results.length === 0 && (
                        <div className="text-center py-12">
                          <div className="text-4xl mb-4">🏡</div>
                          <h3 className="text-xl font-semibold text-gray-900 mb-2">
                            No properties found
                          </h3>
                          <p className="text-gray-600 mb-6">
                            Try adjusting your search filters or search in a different location.
                          </p>
                          <button
                            onClick={handleClearFilters}
                            className="btn-primary"
                          >
                            Clear All Filters
                          </button>
                        </div>
                      )}

                      {/* Pagination */}
                      {data.total_pages > 1 && (
                        <div className="mt-8 flex justify-center">
                          <nav className="flex items-center space-x-2">
                            <button
                              onClick={() => handlePageChange(filters.page - 1)}
                              disabled={filters.page === 1}
                              className="px-3 py-2 rounded-md border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                            >
                              Previous
                            </button>
                            
                            {Array.from({ length: Math.min(5, data.total_pages) }, (_, i) => {
                              const pageNum = i + 1
                              return (
                                <button
                                  key={pageNum}
                                  onClick={() => handlePageChange(pageNum)}
                                  className={`px-3 py-2 rounded-md ${filters.page === pageNum ? 'bg-primary-600 text-white' : 'border border-gray-300 hover:bg-gray-50'}`}
                                >
                                  {pageNum}
                                </button>
                              )
                            })}
                            
                            {data.total_pages > 5 && <span className="px-3">...</span>}
                            
                            <button
                              onClick={() => handlePageChange(filters.page + 1)}
                              disabled={filters.page === data.total_pages}
                              className="px-3 py-2 rounded-md border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                            >
                              Next
                            </button>
                          </nav>
                        </div>
                      )}
                    </>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Quick Search Links */}
          {!isLoading && data?.results.length === 0 && (
            <div className="mt-12">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Popular Searches
              </h3>
              <div className="flex flex-wrap gap-3">
                {[
                  { label: 'Chennai', type: 'city', city: 'Chennai' },
                  { label: 'Coimbatore', type: 'city', city: 'Coimbatore' },
                  { label: 'Bangalore', type: 'city', city: 'Bangalore' },
                  { label: 'Residential Plots', type: 'property_type', property_type: ['plot'] },
                  { label: 'Commercial Spaces', type: 'property_type', property_type: ['commercial'] },
                  { label: 'Agricultural Land', type: 'property_type', property_type: ['agricultural'] },
                ].map((search) => (
                  <button
                    key={search.label}
                    onClick={() => {
                      if (search.type === 'city') {
                        handleSearch({ city: search.city, page: 1 })
                      } else if (search.type === 'property_type') {
                        handleSearch({ property_type: search.property_type, page: 1 })
                      }
                    }}
                    className="px-4 py-2 bg-white border border-gray-300 rounded-full text-sm hover:bg-gray-50"
                  >
                    {search.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

export default SearchPage