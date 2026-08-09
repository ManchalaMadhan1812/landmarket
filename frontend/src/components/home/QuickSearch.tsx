import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLocationStore } from '../../stores/locationStore'

const QuickSearch: React.FC = () => {
  const navigate = useNavigate()
  const { selectedLocation } = useLocationStore()
  const [locationQuery, setLocationQuery] = useState('')

  const popularCities = [
    { name: 'Chennai', state: 'Tamil Nadu' },
    { name: 'Coimbatore', state: 'Tamil Nadu' },
    { name: 'Bangalore', state: 'Karnataka' },
    { name: 'Hyderabad', state: 'Telangana' },
    { name: 'Mumbai', state: 'Maharashtra' },
    { name: 'Delhi', state: 'Delhi' },
    { name: 'Kolkata', state: 'West Bengal' },
  ]

  const propertyTypes = [
    { type: 'residential', label: 'Residential', icon: '🏠' },
    { type: 'commercial', label: 'Commercial', icon: '🏢' },
    { type: 'agricultural', label: 'Agricultural', icon: '🌾' },
    { type: 'plot', label: 'Plots', icon: '📍' },
  ]

  const purposes = [
    { purpose: 'sale', label: 'For Sale', color: 'bg-green-100 text-green-800' },
    { purpose: 'rent', label: 'For Rent', color: 'bg-blue-100 text-blue-800' },
    { purpose: 'lease', label: 'For Lease', color: 'bg-purple-100 text-purple-800' },
  ]

  const handleCitySearch = (city: string) => {
    navigate(`/search?city=${city}`)
  }

  const handlePropertyTypeSearch = (propertyType: string) => {
    navigate(`/search?property_type=${propertyType}`)
  }

  const handlePurposeSearch = (purpose: string) => {
    navigate(`/search?purpose=${purpose}`)
  }

  const handleQuickSearch = () => {
    if (locationQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(locationQuery)}`)
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 mb-8">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-3">
          Find Your Perfect Property
        </h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Search through thousands of verified properties across India. Residential, commercial, agricultural land, and more.
        </p>
      </div>

      {/* Main Search Bar */}
      <div className="max-w-3xl mx-auto mb-8">
        <div className="relative">
          <input
            type="text"
            value={locationQuery}
            onChange={(e) => setLocationQuery(e.target.value)}
            placeholder="Enter city, area, or property type"
            className="input text-lg pl-12 pr-4 py-4 w-full rounded-xl border-2 border-gray-300 focus:border-primary-500 focus:ring-primary-500"
            onKeyPress={(e) => e.key === 'Enter' && handleQuickSearch()}
          />
          <div className="absolute left-4 top-4 text-2xl">🔍</div>
          <button
            onClick={handleQuickSearch}
            className="absolute right-2 top-2 btn-primary px-6 py-3 text-lg rounded-lg"
          >
            Search
          </button>
        </div>

        {selectedLocation && (
          <div className="mt-4 flex items-center justify-center text-sm text-gray-600">
            <span className="mr-2">📍</span>
            Searching near <span className="font-medium ml-1">{selectedLocation.city}</span>
            <button
              onClick={() => navigate(`/search?latitude=${selectedLocation.latitude}&longitude=${selectedLocation.longitude}`)}
              className="ml-2 text-primary-600 hover:text-primary-700 font-medium"
            >
              View properties in this area
            </button>
          </div>
        )}
      </div>

      {/* Property Types */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Browse by Property Type
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {propertyTypes.map((item) => (
            <button
              key={item.type}
              onClick={() => handlePropertyTypeSearch(item.type)}
              className="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
            >
              <span className="text-3xl mb-2">{item.icon}</span>
              <span className="font-medium text-gray-900">{item.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Purpose */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Browse by Purpose
        </h3>
        <div className="flex flex-wrap gap-3">
          {purposes.map((item) => (
            <button
              key={item.purpose}
              onClick={() => handlePurposeSearch(item.purpose)}
              className={`px-4 py-2 rounded-lg font-medium ${item.color} hover:opacity-90 transition-opacity`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Popular Cities */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Popular Cities
          </h3>
          <button
            onClick={() => navigate('/search')}
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            View all cities →
          </button>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
          {popularCities.map((city) => (
            <button
              key={city.name}
              onClick={() => handleCitySearch(city.name)}
              className="flex flex-col items-center p-3 bg-white border border-gray-200 rounded-lg hover:border-primary-300 hover:shadow-sm transition-all"
            >
              <span className="text-lg mb-1">🏙️</span>
              <span className="font-medium text-gray-900">{city.name}</span>
              <span className="text-xs text-gray-500">{city.state}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Advanced Search Link */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-1">
              Need more specific search?
            </h4>
            <p className="text-gray-600">
              Use our advanced filters for price, area, amenities, and more
            </p>
          </div>
          <button
            onClick={() => navigate('/search')}
            className="btn-primary px-6 py-3"
          >
            Advanced Search
          </button>
        </div>
      </div>
    </div>
  )
}

export default QuickSearch