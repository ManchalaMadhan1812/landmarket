import React from 'react'
import { Helmet } from 'react-helmet-async'

const MessagesPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Messages - LandMarket</title>
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Messages</h1>
          
          <div className="text-center py-20">
            <p className="text-gray-600">Real-time messaging system - Coming Soon!</p>
          </div>
        </div>
      </div>
    </>
  )
}

export default MessagesPage