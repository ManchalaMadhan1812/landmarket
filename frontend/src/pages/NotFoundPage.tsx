import React from 'react'
import { Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'

const NotFoundPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Page Not Found - LandMarket</title>
      </Helmet>

      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🏠</div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
          <h2 className="text-xl text-gray-600 mb-8">
            Oops! This property doesn't exist
          </h2>
          <Link
            to="/"
            className="btn-primary"
          >
            Go Back Home
          </Link>
        </div>
      </div>
    </>
  )
}

export default NotFoundPage