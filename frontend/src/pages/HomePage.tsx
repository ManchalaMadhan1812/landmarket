import React from 'react'
import { Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import QuickSearch from '../components/home/QuickSearch'

const HomePage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>LandMarket - Find Your Perfect Property in India</title>
        <meta name="description" content="Discover and list properties across India. Buy, sell, and rent residential, commercial, and agricultural land with LandMarket." />
      </Helmet>

      <div className="min-h-screen">
        {/* Hero Section */}
        <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h1 className="text-4xl md:text-6xl font-bold mb-6">
                Find Your Perfect Property
              </h1>
              <p className="text-xl md:text-2xl text-primary-100 mb-8 max-w-3xl mx-auto">
                Discover verified properties across India. From residential plots to commercial spaces, find your next investment opportunity.
              </p>
              
              {/* Quick Search Bar */}
              <div className="max-w-2xl mx-auto bg-white rounded-xl p-6 shadow-xl">
                <div className="flex flex-col md:flex-row gap-4">
                  <input
                    type="text"
                    placeholder="Search by location, property type..."
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-lg"
                  />
                  <Link
                    to="/search"
                    className="btn-primary px-8 py-3 whitespace-nowrap text-lg font-semibold rounded-lg"
                  >
                    Advanced Search
                  </Link>
                </div>
                <div className="mt-4 text-sm text-gray-600 text-center">
                  Try searching for "Chennai apartments", "Bangalore commercial spaces", or "Agricultural land Tamil Nadu"
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Search Section */}
        <section className="py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <QuickSearch />
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Why Choose LandMarket?
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                We make property transactions simple, secure, and transparent with features designed for the Indian market.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center p-6">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🏡</span>
                </div>
                <h3 className="text-xl font-semibold mb-2">Verified Properties</h3>
                <p className="text-gray-600">
                  All listings are verified with proper documentation including Patta, Chitta, and EC records.
                </p>
              </div>

              <div className="text-center p-6">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🗺️</span>
                </div>
                <h3 className="text-xl font-semibold mb-2">Advanced Search</h3>
                <p className="text-gray-600">
                  Search with maps, filters, and location-based recommendations to find exactly what you need.
                </p>
              </div>

              <div className="text-center p-6">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">💬</span>
                </div>
                <h3 className="text-xl font-semibold mb-2">Direct Communication</h3>
                <p className="text-gray-600">
                  Connect directly with property owners and brokers through our secure messaging platform.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Property Types */}
        <section className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Explore Property Types
              </h2>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { name: 'Residential', icon: '🏠', count: '1,200+' },
                { name: 'Commercial', icon: '🏢', count: '800+' },
                { name: 'Agricultural', icon: '🌾', count: '600+' },
                { name: 'Industrial', icon: '🏭', count: '400+' },
              ].map((type) => (
                <Link
                  key={type.name}
                  to={`/search?type=${type.name.toLowerCase()}`}
                  className="bg-white rounded-lg p-6 text-center hover:shadow-md transition-shadow"
                >
                  <div className="text-4xl mb-4">{type.icon}</div>
                  <h3 className="text-lg font-semibold mb-1">{type.name}</h3>
                  <p className="text-sm text-gray-600">{type.count} properties</p>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-primary-600 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
              Join thousands of property buyers and sellers on LandMarket today.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/auth/register"
                className="btn bg-white text-primary-600 hover:bg-gray-100 px-8 py-3"
              >
                Sign Up Free
              </Link>
              <Link
                to="/search"
                className="btn border border-white text-white hover:bg-white hover:text-primary-600 px-8 py-3"
              >
                Browse Properties
              </Link>
            </div>
          </div>
        </section>
      </div>
    </>
  )
}

export default HomePage