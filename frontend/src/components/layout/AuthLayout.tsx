import React from 'react'
import { Outlet, Navigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

const AuthLayout: React.FC = () => {
  const { isAuthenticated } = useAuthStore()

  // Redirect authenticated users to dashboard
  if (isAuthenticated) {
    return <Navigate to="/app/dashboard" replace />
  }

  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-600 to-primary-800 relative">
        <div className="absolute inset-0 bg-black opacity-20" />
        <div className="relative z-10 flex flex-col justify-center px-12 text-white">
          <h1 className="text-4xl font-bold mb-6">
            Welcome to LandMarket
          </h1>
          <p className="text-xl text-primary-100 mb-8">
            India's premier real estate marketplace. Find your perfect property or list your land with ease.
          </p>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <span className="w-2 h-2 bg-white rounded-full" />
              <span>Verified properties across India</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="w-2 h-2 bg-white rounded-full" />
              <span>Advanced search with maps and filters</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="w-2 h-2 bg-white rounded-full" />
              <span>Direct communication with property owners</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Auth Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <Outlet />
        </div>
      </div>
    </div>
  )
}

export default AuthLayout