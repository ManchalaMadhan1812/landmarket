import React from 'react'
import { ChevronDownIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface FilterProps {
  filters: any
  aggregations?: any
  onFilterChange: (filters: any) => void
  onClearFilters: () => void
}

const SearchFilters: React.FC<FilterProps> = ({
  filters,
  aggregations,
  onFilterChange,
  onClearFilters,
}) => {
  const propertyTypes = [
    { value: 'residential', label: 'Residential' },
    { value: 'commercial', label: 'Commercial' },
    { value: 'industrial', label: 'Industrial' },
    { value: 'agricultural', label: 'Agricultural' },
    { value: 'plot', label: 'Plot' },
    { value: 'apartment', label: 'Apartment' },
    { value: 'house', label: 'House' },
  ]

  const purposes = [
    { value: 'sale', label: 'Sale' },
    { value: 'rent', label: 'Rent' },
    { value: 'lease', label: 'Lease' },
  ]

  const sortOptions = [
    { value: 'relevance', label: 'Relevance' },
    { value: 'price_low', label: 'Price: Low to High' },
    { value: 'price_high', label: 'Price: High to Low' },
    { value: 'newest', label: 'Newest First' },
    { value: 'popular', label: 'Most Popular' },
  ]

  const priceRanges = [
    { label: 'Under ₹10L', min: 0, max: 1000000 },
    { label: '₹10L - ₹25L', min: 1000000, max: 2500000 },
    { label: '₹25L - ₹50L', min: 2500000, max: 5000000 },
    { label: '₹50L - ₹1Cr', min: 5000000, max: 10000000 },
    { label: 'Over ₹1Cr', min: 10000000, max: Infinity },
  ]

  const areaRanges = [
    { label: 'Under 500 sqft', min: 0, max: 500 },
    { label: '500 - 1000 sqft', min: 500, max: 1000 },
    { label: '1000 - 2500 sqft', min: 1000, max: 2500 },
    { label: '2500 - 5000 sqft', min: 2500, max: 5000 },
    { label: 'Over 5000 sqft', min: 5000, max: Infinity },
  ]

  const amenitiesOptions = [
    { value: 'parking', label: 'Parking' },
    { value: 'water_supply', label: 'Water Supply' },
    { value: 'electricity', label: 'Electricity' },
    { value: 'security', label: 'Security' },
    { value: 'garden', label: 'Garden' },
    { value: 'paved_road', label: 'Paved Road' },
    { value: 'near_school', label: 'Near School' },
    { value: 'near_hospital', label: 'Near Hospital' },
    { value: 'borewell', label: 'Borewell' },
    { value: 'boundary_wall', label: 'Boundary Wall' },
  ]

  const hasActiveFilters = () => {
    return (
      filters.property_type?.length > 0 ||
      filters.purpose?.length > 0 ||
      filters.min_price ||
      filters.max_price ||
      filters.min_area ||
      filters.max_area ||
      filters.amenities?.length > 0
    )
  }

  const handlePropertyTypeChange = (type: string) => {
    const currentTypes = filters.property_type || []
    const newTypes = currentTypes.includes(type)
      ? currentTypes.filter((t: string) => t !== type)
      : [...currentTypes, type]
    
    onFilterChange({ property_type: newTypes })
  }

  const handlePurposeChange = (purpose: string) => {
    const currentPurposes = filters.purpose || []
    const newPurposes = currentPurposes.includes(purpose)
      ? currentPurposes.filter((p: string) => p !== purpose)
      : [...currentPurposes, purpose]
    
    onFilterChange({ purpose: newPurposes })
  }

  const handleAmenityChange = (amenity: string) => {
    const currentAmenities = filters.amenities || []
    const newAmenities = currentAmenities.includes(amenity)
      ? currentAmenities.filter((a: string) => a !== amenity)
      : [...currentAmenities, amenity]
    
    onFilterChange({ amenities: newAmenities })
  }

  const handlePriceRangeClick = (min: number, max: number) => {
    onFilterChange({
      min_price: min,
      max_price: max === Infinity ? undefined : max,
    })
  }

  const handleAreaRangeClick = (min: number, max: number) => {
    onFilterChange({
      min_area: min,
      max_area: max === Infinity ? undefined : max,
    })
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
        {hasActiveFilters() && (
          <button
            onClick={onClearFilters}
            className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
          >
            <XMarkIcon className="h-4 w-4" />
            Clear All
          </button>
        )}
      </div>

      {/* Sort By */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Sort By
        </label>
        <select
          value={filters.sort_by}
          onChange={(e) => onFilterChange({ sort_by: e.target.value })}
          className="input w-full"
        >
          {sortOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Property Type */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="text-sm font-medium text-gray-700">
            Property Type
          </label>
          {aggregations?.property_types && (
            <span className="text-sm text-gray-500">
              {Object.values(aggregations.property_types).reduce((sum: number, count: any) => sum + count, 0)} properties
            </span>
          )}
        </div>
        <div className="space-y-2">
          {propertyTypes.map((type) => {
            const isSelected = filters.property_type?.includes(type.value)
            const count = aggregations?.property_types?.[type.value] || 0
            
            return (
              <button
                key={type.value}
                onClick={() => handlePropertyTypeChange(type.value)}
                className={`flex items-center justify-between w-full text-left py-2 px-3 rounded-md ${
                  isSelected
                    ? 'bg-primary-50 text-primary-700'
                    : 'hover:bg-gray-50'
                }`}
              >
                <span className="text-sm">{type.label}</span>
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                  {count}
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Purpose */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="text-sm font-medium text-gray-700">
            Purpose
          </label>
          {aggregations?.purposes && (
            <span className="text-sm text-gray-500">
              {Object.values(aggregations.purposes).reduce((sum: number, count: any) => sum + count, 0)} properties
            </span>
          )}
        </div>
        <div className="grid grid-cols-3 gap-2">
          {purposes.map((purpose) => {
            const isSelected = filters.purpose?.includes(purpose.value)
            const count = aggregations?.purposes?.[purpose.value] || 0
            
            return (
              <button
                key={purpose.value}
                onClick={() => handlePurposeChange(purpose.value)}
                className={`py-2 text-center text-sm rounded-md ${
                  isSelected
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <div className="font-medium">{purpose.label}</div>
                <div className="text-xs mt-1">{count}</div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Price Range */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Price Range
        </label>
        <div className="space-y-2">
          {priceRanges.map((range, index) => (
            <button
              key={index}
              onClick={() => handlePriceRangeClick(range.min, range.max)}
              className={`flex justify-between items-center w-full text-left py-2 px-3 rounded-md ${
                filters.min_price === range.min
                  ? 'bg-primary-50 text-primary-700'
                  : 'hover:bg-gray-50'
              }`}
            >
              <span className="text-sm">{range.label}</span>
              {aggregations?.price_ranges && (
                <span className="text-xs text-gray-500">
                  {aggregations.price_ranges[range.label] || 0}
                </span>
              )}
            </button>
          ))}
        </div>
        
        {/* Custom Price Inputs */}
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Min Price</label>
            <div className="relative">
              <span className="absolute left-3 top-3 text-gray-500 text-sm">₹</span>
              <input
                type="number"
                value={filters.min_price || ''}
                onChange={(e) => onFilterChange({ min_price: e.target.value || undefined })}
                placeholder="Min"
                className="input w-full pl-8"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Max Price</label>
            <div className="relative">
              <span className="absolute left-3 top-3 text-gray-500 text-sm">₹</span>
              <input
                type="number"
                value={filters.max_price || ''}
                onChange={(e) => onFilterChange({ max_price: e.target.value || undefined })}
                placeholder="Max"
                className="input w-full pl-8"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Area Range */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Area Range
        </label>
        <div className="space-y-2">
          {areaRanges.map((range, index) => (
            <button
              key={index}
              onClick={() => handleAreaRangeClick(range.min, range.max)}
              className={`flex justify-between items-center w-full text-left py-2 px-3 rounded-md ${
                filters.min_area === range.min
                  ? 'bg-primary-50 text-primary-700'
                  : 'hover:bg-gray-50'
              }`}
            >
              <span className="text-sm">{range.label}</span>
            </button>
          ))}
        </div>
        
        {/* Custom Area Inputs */}
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Min Area</label>
            <div className="relative">
              <input
                type="number"
                value={filters.min_area || ''}
                onChange={(e) => onFilterChange({ min_area: e.target.value || undefined })}
                placeholder="Min"
                className="input w-full pr-12"
              />
              <span className="absolute right-3 top-3 text-gray-500 text-sm">sqft</span>
            </div>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Max Area</label>
            <div className="relative">
              <input
                type="number"
                value={filters.max_area || ''}
                onChange={(e) => onFilterChange({ max_area: e.target.value || undefined })}
                placeholder="Max"
                className="input w-full pr-12"
              />
              <span className="absolute right-3 top-3 text-gray-500 text-sm">sqft</span>
            </div>
          </div>
        </div>
      </div>

      {/* Amenities */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="text-sm font-medium text-gray-700">
            Amenities
          </label>
          {aggregations?.amenities && (
            <span className="text-sm text-gray-500">
              {Object.keys(aggregations.amenities).length} options
            </span>
          )}
        </div>
        <div className="grid grid-cols-2 gap-2">
          {amenitiesOptions.map((amenity) => {
            const isSelected = filters.amenities?.includes(amenity.value)
            const count = aggregations?.amenities?.[amenity.value] || 0
            
            return (
              <button
                key={amenity.value}
                onClick={() => handleAmenityChange(amenity.value)}
                className={`flex items-center gap-2 py-2 px-3 rounded-md text-sm ${
                  isSelected
                    ? 'bg-primary-50 text-primary-700'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                }`}
              >
                <div className="w-2 h-2 rounded-full bg-current opacity-50" />
                <span>{amenity.label}</span>
                {count > 0 && (
                  <span className="ml-auto text-xs text-gray-500">{count}</span>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Cities Aggregation */}
      {aggregations?.cities && Object.keys(aggregations.cities).length > 0 && (
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-gray-700">
              Popular Cities
            </label>
            <button
              onClick={() => onFilterChange({ city: '' })}
              className="text-xs text-primary-600 hover:text-primary-700"
            >
              Clear
            </button>
          </div>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {Object.entries(aggregations.cities)
              .sort(([, countA], [, countB]) => (countB as number) - (countA as number))
              .slice(0, 10)
              .map(([city, count]) => (
                <button
                  key={city}
                  onClick={() => onFilterChange({ city })}
                  className={`flex justify-between items-center w-full text-left py-2 px-3 rounded-md ${
                    filters.city === city
                      ? 'bg-primary-50 text-primary-700'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <span className="text-sm">{city}</span>
                  <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                    {count as number}
                  </span>
                </button>
              ))}
          </div>
        </div>
      )}

      {/* Apply Filters Button */}
      <button
        onClick={() => onFilterChange({})}
        className="btn-primary w-full"
      >
        Apply Filters
      </button>
    </div>
  )
}

export default SearchFilters