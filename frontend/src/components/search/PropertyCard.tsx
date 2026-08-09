import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { HeartIcon, EyeIcon, MapPinIcon, CheckIcon, PlusIcon } from '@heroicons/react/24/outline'
import { HeartIcon as HeartIconSolid } from '@heroicons/react/24/solid'
import { useAuthStore } from '../../stores/authStore'
import { useCompareStore } from '../../stores/compareStore'
import toast from 'react-hot-toast'

interface PropertyCardProps {
  property: {
    id: string
    title: string
    price: number
    city: string
    state: string
    property_type: string
    purpose: string
    total_area: number
    area_unit: string
    verification_score: number
    view_count: number
    save_count: number
    avg_rating: number
    primary_image?: string
    is_saved?: boolean
  }
  onSave?: (propertyId: string) => void
}

const PropertyCard: React.FC<PropertyCardProps> = ({
  property,
  onSave,
}) => {
  const { isAuthenticated } = useAuthStore()
  const [isSaved, setIsSaved] = useState(property.is_saved || false)
  const { addProperty, removeProperty, isComparing } = useCompareStore()
  const currentlyComparing = isComparing(property.id)

  const formatPrice = (price: number) => {
    if (price >= 10000000) {
      return `₹${(price / 10000000).toFixed(2)} Cr`
    } else if (price >= 100000) {
      return `₹${(price / 100000).toFixed(2)} L`
    } else {
      return `₹${price.toLocaleString()}`
    }
  }

  const getPropertyTypeIcon = () => {
    switch (property.property_type) {
      case 'residential': return '🏠'
      case 'commercial': return '🏢'
      case 'agricultural': return '🌾'
      case 'industrial': return '🏭'
      case 'plot': return '📍'
      case 'apartment': return '🏢'
      case 'house': return '🏡'
      default: return '🏠'
    }
  }

  const getPurposeColor = () => {
    switch (property.purpose) {
      case 'sale': return 'bg-green-100 text-green-800'
      case 'rent': return 'bg-blue-100 text-blue-800'
      case 'lease': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const handleSaveClick = () => {
    if (!isAuthenticated) {
      // TODO: Show login modal
      return
    }
    setIsSaved(!isSaved)
    onSave(property.id)
  }

  const handleCompareClick = () => {
    if (currentlyComparing) {
      removeProperty(property.id)
      toast.success('Removed from comparison')
    } else {
      addProperty(property.id)
      toast.success('Added to comparison bar')
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-300">
      {/* Property Image */}
      <div className="relative h-48 bg-gray-100">
        {property.primary_image ? (
          <img
            src={property.primary_image}
            alt={property.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-4xl">{getPropertyTypeIcon()}</span>
          </div>
        )}
        
        {/* Save Button */}
        <button
          onClick={handleSaveClick}
          className="absolute top-3 right-3 p-2 bg-white rounded-full shadow-md hover:bg-gray-50"
        >
          {isSaved ? (
            <HeartIconSolid className="h-5 w-5 text-red-500" />
          ) : (
            <HeartIcon className="h-5 w-5 text-gray-600" />
          )}
        </button>

        {/* Property Type Badge */}
        <div className="absolute top-3 left-3 px-3 py-1 bg-black bg-opacity-50 text-white text-xs rounded-full">
          {property.property_type.charAt(0).toUpperCase() + property.property_type.slice(1)}
        </div>

        {/* Verification Badge */}
        {property.verification_score >= 80 && (
          <div className="absolute bottom-3 left-3 px-3 py-1 bg-green-500 text-white text-xs rounded-full font-medium">
            ✓ Verified
          </div>
        )}
      </div>

      {/* Property Details */}
      <div className="p-4">
        {/* Price and Title */}
        <div className="mb-3">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-1">
                {property.title}
              </h3>
              <div className="text-2xl font-bold text-gray-900">
                {formatPrice(property.price)}
              </div>
              <div className="text-sm text-gray-600">
                {property.total_area} {property.area_unit} • {property.purpose}
              </div>
            </div>
            <span className={`px-2 py-1 rounded text-xs font-medium ${getPurposeColor()}`}>
              {property.purpose.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Location */}
        <div className="flex items-center text-gray-600 mb-3">
          <MapPinIcon className="h-4 w-4 mr-1" />
          <span className="text-sm">
            {property.city}, {property.state}
          </span>
        </div>

        {/* Stats */}
        <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <EyeIcon className="h-4 w-4" />
              <span>{property.view_count}</span>
            </div>
            <div className="flex items-center gap-1">
              <HeartIcon className="h-4 w-4" />
              <span>{property.save_count}</span>
            </div>
            {property.avg_rating > 0 && (
              <div className="flex items-center gap-1">
                <span className="text-yellow-500">★</span>
                <span>{property.avg_rating.toFixed(1)}</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            {/* Verification Score */}
            {property.verification_score > 0 && (
              <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${property.verification_score >= 80 ? 'bg-green-500' : property.verification_score >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                  style={{ width: `${property.verification_score}%` }}
                />
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Link
            to={`/property/${property.id}`}
            className="btn-primary flex-1 text-center py-2"
          >
            View Details
          </Link>
          <button
            onClick={handleCompareClick}
            className={`btn-outline py-2 px-3 flex items-center justify-center gap-1 font-medium transition-colors ${
              currentlyComparing ? 'bg-primary-50 text-primary-700 border-primary-300' : 'text-gray-700'
            }`}
          >
            {currentlyComparing ? (
              <>
                <CheckIcon className="w-4 h-4 text-primary-600" />
                <span>Comparing</span>
              </>
            ) : (
              <>
                <PlusIcon className="w-4 h-4 text-gray-500" />
                <span>Compare</span>
              </>
            )}
          </button>
        </div>

        {/* Quick Info */}
        <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-2 gap-2 text-xs">
          <div className="text-gray-600">ID:</div>
          <div className="text-gray-900 font-medium">{property.id.slice(0, 8)}...</div>
          
          <div className="text-gray-600">Type:</div>
          <div className="text-gray-900 capitalize">{property.property_type}</div>
          
          <div className="text-gray-600">Area:</div>
          <div className="text-gray-900">{property.total_area} {property.area_unit}</div>
          
          <div className="text-gray-600">Trust Score:</div>
          <div className="text-gray-900">{property.verification_score}%</div>
        </div>
      </div>
    </div>
  )
}

export default PropertyCard