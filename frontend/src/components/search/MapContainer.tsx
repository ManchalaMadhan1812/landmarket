import React, { useEffect, useState } from 'react'
import { GoogleMap, LoadScript, Marker, InfoWindow } from '@react-google-maps/api'

interface Property {
  id: string
  title: string
  price: number
  city: string
  location?: {
    lat: number
    lon: number
  }
}

interface MapContainerProps {
  properties: Property[]
  center: {
    lat: number
    lng: number
  }
  zoom: number
  onPropertyClick?: (property: Property) => void
}

const MapContainer: React.FC<MapContainerProps> = ({
  properties,
  center,
  zoom,
  onPropertyClick,
}) => {
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null)
  const [mapInstance, setMapInstance] = useState<any>(null)
  const [mapReady, setMapReady] = useState(false)
  const [clusteredMarkers, setClusteredMarkers] = useState<Property[]>([])

  const mapContainerStyle = {
    width: '100%',
    height: '600px',
  }

  const options = {
    disableDefaultUI: false,
    zoomControl: true,
    streetViewControl: true,
    mapTypeControl: true,
    fullscreenControl: true,
    styles: [
      {
        featureType: 'poi',
        elementType: 'labels',
        stylers: [{ visibility: 'off' }],
      },
    ],
  }

  // Simple clustering - group properties that are too close together
  useEffect(() => {
    if (properties.length === 0) {
      setClusteredMarkers([])
      return
    }

    const clusterRadius = 0.005 // ~500 meters at equator
    const clusters: Property[] = []
    const used = new Set()

    properties.forEach((property, index) => {
      if (used.has(index) || !property.location) return

      const cluster = [property]
      used.add(index)

      // Find nearby properties
      properties.slice(index + 1).forEach((otherProp, otherIndex) => {
        if (!otherProp.location) return
        
        const distance = Math.sqrt(
          Math.pow(otherProp.location.lat - property.location.lat, 2) +
          Math.pow(otherProp.location.lon - property.location.lon, 2)
        )

        if (distance < clusterRadius && !used.has(index + otherIndex + 1)) {
          cluster.push(otherProp)
          used.add(index + otherIndex + 1)
        }
      })

      // Use first property as cluster representative
      clusters.push(cluster[0])
    })

    setClusteredMarkers(clusters)
  }, [properties])

  const formatPrice = (price: number) => {
    if (price >= 10000000) {
      return `₹${(price / 10000000).toFixed(2)} Cr`
    } else if (price >= 100000) {
      return `₹${(price / 100000).toFixed(2)} L`
    } else {
      return `₹${price.toLocaleString()}`
    }
  }

  const getMarkerIcon = (propertyType: string) => {
    const color = propertyType === 'sale' ? 'green' : propertyType === 'rent' ? 'blue' : 'orange'
    
    return {
      path: 'M0-48c-9.8 0-17.7 7.8-17.7 17.4 0 15.5 17.7 30.6 17.7 30.6s17.7-15.4 17.7-30.6c0-9.6-7.9-17.4-17.7-17.4z',
      fillColor: color,
      fillOpacity: 0.8,
      scale: 1,
      strokeColor: '#FFFFFF',
      strokeWeight: 2,
    }
  }

  const getPropertyTypeColor = (propertyType: string) => {
    switch (propertyType) {
      case 'residential': return '#3B82F6' // Blue
      case 'commercial': return '#10B981' // Green
      case 'agricultural': return '#F59E0B' // Yellow
      case 'industrial': return '#EF4444' // Red
      case 'plot': return '#8B5CF6' // Purple
      default: return '#6B7280' // Gray
    }
  }

  const handleMapLoad = (map: any) => {
    setMapInstance(map)
    setMapReady(true)
  }

  const handleMarkerClick = (property: Property) => {
    setSelectedProperty(property)
    if (onPropertyClick) {
      onPropertyClick(property)
    }
  }

  const handleInfoWindowClose = () => {
    setSelectedProperty(null)
  }

  const fitBoundsToMarkers = () => {
    if (!mapInstance || clusteredMarkers.length === 0) return

    const bounds = new window.google.maps.LatLngBounds()
    clusteredMarkers.forEach((property) => {
      if (property.location) {
        bounds.extend(new window.google.maps.LatLng(property.location.lat, property.location.lon))
      }
    })

    mapInstance.fitBounds(bounds)
  }

  if (!window.google || !process.env.REACT_APP_GOOGLE_MAPS_API_KEY) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
        <div className="text-center">
          <div className="text-3xl mb-4">🗺️</div>
          <p className="text-gray-600 mb-2">Google Maps is not configured</p>
          <p className="text-sm text-gray-500">
            Add REACT_APP_GOOGLE_MAPS_API_KEY to your environment variables
          </p>
        </div>
      </div>
    )
  }

  return (
    <LoadScript
      googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY || ''}
      libraries={['places', 'geometry']}
    >
      <GoogleMap
        mapContainerStyle={mapContainerStyle}
        center={center}
        zoom={zoom}
        options={options}
        onLoad={handleMapLoad}
      >
        {/* Current Location Marker */}
        <Marker
          position={center}
          icon={{
            path: window.google.maps.SymbolPath.CIRCLE,
            scale: 8,
            fillColor: '#2563EB',
            fillOpacity: 0.8,
            strokeColor: '#FFFFFF',
            strokeWeight: 2,
          }}
        />

        {/* Property Markers */}
        {clusteredMarkers.map((property) => {
          if (!property.location) return null

          return (
            <Marker
              key={property.id}
              position={{
                lat: property.location.lat,
                lng: property.location.lon,
              }}
              icon={{
                ...getMarkerIcon(property.id),
                fillColor: getPropertyTypeColor(property.property_type),
              }}
              onClick={() => handleMarkerClick(property)}
            />
          )
        })}

        {/* Info Window */}
        {selectedProperty && selectedProperty.location && (
          <InfoWindow
            position={{
              lat: selectedProperty.location.lat,
              lng: selectedProperty.location.lon,
            }}
            onCloseClick={handleInfoWindowClose}
          >
            <div className="max-w-xs">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {selectedProperty.title}
              </h3>
              <div className="text-2xl font-bold text-gray-900 mb-2">
                {formatPrice(selectedProperty.price)}
              </div>
              <div className="text-sm text-gray-600 mb-3">
                {selectedProperty.city}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => window.location.href = `/property/${selectedProperty.id}`}
                  className="btn-primary btn-sm"
                >
                  View Details
                </button>
                <button
                  onClick={() => {
                    // TODO: Add to comparison
                  }}
                  className="btn-outline btn-sm"
                >
                  Compare
                </button>
              </div>
            </div>
          </InfoWindow>
        )}

        {/* Map Controls */}
        {mapReady && (
          <div className="absolute bottom-4 right-4 bg-white rounded-lg shadow-lg p-3 space-y-2">
            <button
              onClick={fitBoundsToMarkers}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded w-full"
              title="Fit to properties"
            >
              <span className="text-lg">📍</span>
              Fit to Properties
            </button>
            <div className="text-xs text-gray-500 pt-2 border-t">
              {clusteredMarkers.length} of {properties.length} properties shown
            </div>
          </div>
        )}

        {/* Legend */}
        <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-3">
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Property Types</h4>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span className="text-xs text-gray-600">Residential</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-xs text-gray-600">Commercial</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <span className="text-xs text-gray-600">Agricultural</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span className="text-xs text-gray-600">Industrial</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-purple-500"></div>
              <span className="text-xs text-gray-600">Plot</span>
            </div>
          </div>
        </div>
      </GoogleMap>
    </LoadScript>
  )
}

export default MapContainer