import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface Location {
  latitude: number
  longitude: number
  address?: string
  city?: string
  state?: string
  country?: string
}

interface LocationState {
  currentLocation: Location | null
  selectedLocation: Location | null
  permissionGranted: boolean
  isLoading: boolean
  error: string | null
  
  // Actions
  setCurrentLocation: (location: Location) => void
  setSelectedLocation: (location: Location) => void
  setPermissionGranted: (granted: boolean) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  requestLocation: () => Promise<void>
  clearError: () => void
}

export const useLocationStore = create<LocationState>()(
  persist(
    (set, get) => ({
      currentLocation: null,
      selectedLocation: null,
      permissionGranted: false,
      isLoading: false,
      error: null,

      setCurrentLocation: (location: Location) => {
        set({ currentLocation: location, error: null })
      },

      setSelectedLocation: (location: Location) => {
        set({ selectedLocation: location })
      },

      setPermissionGranted: (granted: boolean) => {
        set({ permissionGranted: granted })
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      },

      setError: (error: string | null) => {
        set({ error, isLoading: false })
      },

      clearError: () => {
        set({ error: null })
      },

      requestLocation: async () => {
        const state = get()
        
        if (state.isLoading) return
        
        set({ isLoading: true, error: null })

        try {
          if (!navigator.geolocation) {
            throw new Error('Geolocation is not supported by this browser')
          }

          const position = await new Promise<GeolocationPosition>((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
              resolve,
              reject,
              {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000 // 5 minutes
              }
            )
          })

          const location: Location = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          }

          // Reverse geocode to get address (optional)
          try {
            const response = await fetch(
              `https://maps.googleapis.com/maps/api/geocode/json?latlng=${location.latitude},${location.longitude}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY}`
            )
            
            if (response.ok) {
              const data = await response.json()
              if (data.results && data.results.length > 0) {
                const result = data.results[0]
                const addressComponents = result.address_components
                
                location.address = result.formatted_address
                location.city = addressComponents.find((c: any) => 
                  c.types.includes('locality') || c.types.includes('administrative_area_level_2')
                )?.long_name
                location.state = addressComponents.find((c: any) => 
                  c.types.includes('administrative_area_level_1')
                )?.long_name
                location.country = addressComponents.find((c: any) => 
                  c.types.includes('country')
                )?.long_name
              }
            }
          } catch (geocodeError) {
            console.warn('Reverse geocoding failed:', geocodeError)
            // Continue without address information
          }

          set({
            currentLocation: location,
            selectedLocation: location,
            permissionGranted: true,
            isLoading: false,
            error: null,
          })
        } catch (error) {
          let errorMessage = 'Unable to get your location'
          
          if (error instanceof GeolocationPositionError) {
            switch (error.code) {
              case error.PERMISSION_DENIED:
                errorMessage = 'Location access denied. Please enable location permissions.'
                set({ permissionGranted: false })
                break
              case error.POSITION_UNAVAILABLE:
                errorMessage = 'Location information is unavailable.'
                break
              case error.TIMEOUT:
                errorMessage = 'Location request timed out. Please try again.'
                break
            }
          }

          set({
            error: errorMessage,
            isLoading: false,
            permissionGranted: false,
          })
        }
      },
    }),
    {
      name: 'landmarket-location',
      partialize: (state) => ({
        selectedLocation: state.selectedLocation,
        permissionGranted: state.permissionGranted,
      }),
    }
  )
)