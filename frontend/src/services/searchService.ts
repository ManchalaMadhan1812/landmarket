import api from './api'

export interface SearchFilters {
  q?: string
  city?: string
  property_type?: string[]
  purpose?: string[]
  min_price?: number | string
  max_price?: number | string
  min_area?: number | string
  max_area?: number | string
  amenities?: string[]
  latitude?: number
  longitude?: number
  radius_km?: number
  sort_by?: string
  page?: number
  page_size?: number
  survey_number?: string
  patta_number?: string
  ids?: string[]
}

export interface SearchResult {
  count: number
  total_pages: number
  current_page: number
  results: PropertyResult[]
  aggregations?: {
    property_types?: Record<string, number>
    purposes?: Record<string, number>
    cities?: Record<string, number>
    price_ranges?: Record<string, number>
    amenities?: Record<string, number>
  }
}

export interface PropertyResult {
  id: string
  title: string
  description: string
  price: number
  city: string
  state: string
  property_type: string
  purpose: string
  total_area: number
  area_unit: string
  primary_image?: string
  verification_score: number
  view_count: number
  save_count: number
  avg_rating: number
  created_at: string
  updated_at: string
  location?: {
    lat: number
    lon: number
  }
}

export interface NearbyProperty {
  id: string
  title: string
  price: number
  distance_km: number
  location: {
    lat: number
    lon: number
  }
}

export interface LocationSuggestion {
  id: string
  name: string
  type: 'city' | 'area' | 'landmark'
  state?: string
  coordinates?: {
    latitude: number
    longitude: number
  }
}

/**
 * Search properties with filters
 */
export const searchProperties = async (filters: SearchFilters): Promise<SearchResult> => {
  try {
    // Format filters for API
    const params = new URLSearchParams()
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value) && value.length > 0) {
          value.forEach(v => params.append(key, v))
        } else {
          params.append(key, value.toString())
        }
      }
    })

    const response = await api.get(`/api/search/properties?${params}`)
    return response.data
  } catch (error: any) {
    console.error('Search error:', error)
    throw new Error(error.response?.data?.detail || 'Failed to search properties')
  }
}

/**
 * Search properties near a location
 */
export const searchNearbyProperties = async (
  latitude: number,
  longitude: number,
  radius_km: number = 10
): Promise<NearbyProperty[]> => {
  try {
    const response = await api.get('/api/search/nearby', {
      params: {
        latitude,
        longitude,
        radius_km,
      },
    })
    return response.data
  } catch (error: any) {
    console.error('Nearby search error:', error)
    throw new Error(error.response?.data?.detail || 'Failed to find nearby properties')
  }
}

/**
 * Get location suggestions for autocomplete
 */
export const getLocationSuggestions = async (
  query: string,
  limit: number = 10
): Promise<LocationSuggestion[]> => {
  if (!query.trim()) return []

  try {
    const response = await api.get('/api/search/location-autocomplete', {
      params: {
        q: query,
        limit,
      },
    })
    return response.data
  } catch (error: any) {
    console.error('Location suggestions error:', error)
    throw new Error(error.response?.data?.detail || 'Failed to get location suggestions')
  }
}

/**
 * Get search aggregations for filter options
 */
export const getSearchAggregations = async (): Promise<any> => {
  try {
    const response = await api.get('/api/search/aggregations')
    return response.data
  } catch (error: any) {
    console.error('Aggregations error:', error)
    throw new Error(error.response?.data?.detail || 'Failed to get search aggregations')
  }
}

/**
 * Save search preferences for user
 */
export const saveSearchPreferences = async (filters: SearchFilters): Promise<void> => {
  try {
    await api.post('/api/search/preferences', filters)
  } catch (error: any) {
    console.error('Save preferences error:', error)
    // Don't throw for this - it's non-critical
  }
}

/**
 * Get saved searches for user
 */
export const getSavedSearches = async (): Promise<any[]> => {
  try {
    const response = await api.get('/api/search/saved')
    return response.data
  } catch (error: any) {
    console.error('Get saved searches error:', error)
    return []
  }
}

/**
 * Delete a saved search
 */
export const deleteSavedSearch = async (id: string): Promise<void> => {
  try {
    await api.delete(`/api/search/saved/${id}`)
  } catch (error: any) {
    console.error('Delete saved search error:', error)
    throw new Error(error.response?.data?.detail || 'Failed to delete saved search')
  }
}

/**
 * Get search analytics
 */
export const getSearchAnalytics = async (): Promise<any> => {
  try {
    const response = await api.get('/api/search/analytics')
    return response.data
  } catch (error: any) {
    console.error('Search analytics error:', error)
    return {}
  }
}

/**
 * Get popular searches
 */
export const getPopularSearches = async (limit: number = 10): Promise<string[]> => {
  try {
    const response = await api.get('/api/search/popular', {
      params: { limit },
    })
    return response.data
  } catch (error: any) {
    console.error('Popular searches error:', error)
    return []
  }
}

/**
 * Get trending properties
 */
export const getTrendingProperties = async (limit: number = 10): Promise<PropertyResult[]> => {
  try {
    const response = await api.get('/api/search/trending', {
      params: { limit },
    })
    return response.data
  } catch (error: any) {
    console.error('Trending properties error:', error)
    return []
  }
}

/**
 * Get recently viewed properties
 */
export const getRecentlyViewed = async (limit: number = 10): Promise<PropertyResult[]> => {
  try {
    const response = await api.get('/api/search/recently-viewed', {
      params: { limit },
    })
    return response.data
  } catch (error: any) {
    console.error('Recently viewed error:', error)
    return []
  }
}

/**
 * Get recommended properties based on search history
 */
export const getRecommendedProperties = async (limit: number = 10): Promise<PropertyResult[]> => {
  try {
    const response = await api.get('/api/search/recommended', {
      params: { limit },
    })
    return response.data
  } catch (error: any) {
    console.error('Recommended properties error:', error)
    return []
  }
}

export default {
  searchProperties,
  searchNearbyProperties,
  getLocationSuggestions,
  getSearchAggregations,
  saveSearchPreferences,
  getSavedSearches,
  deleteSavedSearch,
  getSearchAnalytics,
  getPopularSearches,
  getTrendingProperties,
  getRecentlyViewed,
  getRecommendedProperties,
}