import React, { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLocationStore } from '../../stores/locationStore'

interface SearchHeaderProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  onLocationSelect: (location: { latitude: number; longitude: number; city?: string }) => void
  selectedLocation: any
}

const SearchHeader: React.FC<SearchHeaderProps> = ({
  searchQuery,
  onSearchChange,
  onLocationSelect,
  selectedLocation,
}) => {
  const navigate = useNavigate()
  const { requestLocation, isLoading } = useLocationStore()
  const [isSearchingLocation, setIsSearchingLocation] = useState(false)
  const [locationQuery, setLocationQuery] = useState('')

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSearchChange(searchQuery)
  }

  const handleLocationClick = useCallback(async () => {
    setIsSearchingLocation(true)
    try {
      await requestLocation()
      if (selectedLocation) {
        onLocationSelect({
          latitude: selectedLocation.latitude,
          longitude: selectedLocation.longitude,
          city: selectedLocation.city,
        })
      }
    } finally {
      setIsSearchingLocation(false)
    }
  }, [requestLocation, selectedLocation, onLocationSelect])

  const handleSearchBySurvey = () => {
    const surveyNumber = prompt('Enter survey number:')
    if (surveyNumber) {
      navigate(`/search?survey_number=${surveyNumber}`)
    }
  }

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Main Search Bar */}
        <form onSubmit={handleSearchSubmit} className="space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Location Search */}
            <div className="flex-1">
              <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
                Location
              </label>
              <div className="relative">
                <input
                  type="text"
                  id="location"
                  value={locationQuery}
                  onChange={(e) => setLocationQuery(e.target.value)}
                  placeholder="Enter city or area"
                  className="input w-full pl-10"
                />
                <div className="absolute left-3 top-3 text-gray-400">
                  📍
                </div>
                <button
                  type="button"
                  onClick={handleLocationClick}
                  disabled={isSearchingLocation || isLoading}
                  className="absolute right-3 top-3 text-sm text-primary-600 hover:text-primary-700 disabled:opacity-50"
                >
                  {isSearchingLocation || isLoading ? 'Locating...' : 'Use My Location'}
                </button>
              </div>
              {selectedLocation && (
                <p className="mt-2 text-sm text-gray-600">
                  Searching near <span className="font-medium">{selectedLocation.city || 'your location'}</span>
                </p>
              )}
            </div>

            {/* Property Search */}
            <div className="flex-1">
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
                Search Properties
              </label>
              <div className="relative">
                <input
                  type="text"
                  id="search"
                  value={searchQuery}
                  onChange={(e) => onSearchChange(e.target.value)}
                  placeholder="What are you looking for?"
                  className="input w-full pl-10"
                />
                <div className="absolute left-3 top-3 text-gray-400">
                  🔍
                </div>
                <button
                  type="submit"
                  className="absolute right-3 top-3 text-primary-600 hover:text-primary-700"
                >
                  Search
                </button>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex flex-wrap gap-3 items-center text-sm">
            <span className="text-gray-600">Quick search:</span>
            <button
              type="button"
              onClick={() => navigate('/search?property_type=residential&purpose=sale')}
              className="px-3 py-1 bg-primary-50 text-primary-700 rounded-full hover:bg-primary-100"
            >
              Residential Sale
            </button>
            <button
              type="button"
              onClick={() => navigate('/search?property_type=commercial&purpose=rent')}
              className="px-3 py-1 bg-primary-50 text-primary-700 rounded-full hover:bg-primary-100"
            >
              Commercial Rent
            </button>
            <button
              type="button"
              onClick={() => navigate('/search?property_type=agricultural&purpose=sale')}
              className="px-3 py-1 bg-primary-50 text-primary-700 rounded-full hover:bg-primary-100"
            >
              Agricultural Land
            </button>
            <button
              type="button"
              onClick={handleSearchBySurvey}
              className="px-3 py-1 bg-green-50 text-green-700 rounded-full hover:bg-green-100 ml-auto"
            >
              Search by Survey Number
            </button>
          </div>
        </form>

        {/* Search Tips */}
        <div className="mt-6 pt-6 border-t border-gray-100">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div className="text-sm text-gray-600">
              <span className="font-medium">Pro Tip:</span> Use advanced filters to narrow down results by price, area, and amenities.
            </div>
            <div className="flex gap-4">
              <button
                onClick={() => navigate('/about')}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                How to Buy Property
              </button>
              <button
                onClick={() => navigate('/auth/register')}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                List Your Property
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SearchHeader