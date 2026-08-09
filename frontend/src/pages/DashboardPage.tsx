import React from 'react'
import { Helmet } from 'react-helmet-async'
import { useAuthStore } from '../stores/authStore'

const DashboardPage: React.FC = () => {
  const { user } = useAuthStore()

  return (
    <>
      <Helmet>
        <title>Dashboard - LandMarket</title>
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome back, {user?.firstName}!
            </h1>
            <p className="text-gray-600">
              Role: {user?.role}
            </p>
          </div>

          <div className="text-center py-20">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Dashboard Coming Soon
            </h2>
            <p className="text-gray-600 mb-4">
              Bento-grid layout with activity tiles, saved properties, and analytics
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="font-semibold mb-2">Saved Properties</h3>
                <p className="text-gray-500 text-sm">Your wishlist and favorites</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="font-semibold mb-2">Recent Activity</h3>
                <p className="text-gray-500 text-sm">Latest searches and views</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="font-semibold mb-2">Messages</h3>
                <p className="text-gray-500 text-sm">Chat with property owners</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default DashboardPage