import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useAuthStore } from '../../stores/authStore'

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuthStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // TODO: Implement actual login API call
      setTimeout(() => {
        // Mock login for development
        const mockUser = {
          id: '1',
          email,
          firstName: 'Demo',
          lastName: 'User',
          role: 'buyer' as const,
          isVerified: true,
        }
        
        login('mock-access-token', 'mock-refresh-token', mockUser)
        setIsLoading(false)
      }, 1000)
    } catch (error) {
      setIsLoading(false)
      console.error('Login error:', error)
    }
  }

  return (
    <>
      <Helmet>
        <title>Login - LandMarket</title>
      </Helmet>

      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Welcome Back</h2>
          <p className="text-gray-600 mt-2">Sign in to your LandMarket account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input w-full"
              placeholder="Enter your email"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input w-full"
              placeholder="Enter your password"
              required
            />
          </div>

          <div className="flex items-center justify-between">
            <label className="flex items-center">
              <input type="checkbox" className="rounded border-gray-300" />
              <span className="ml-2 text-sm text-gray-600">Remember me</span>
            </label>
            <Link
              to="/auth/forgot-password"
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              Forgot password?
            </Link>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary w-full"
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <Link
              to="/auth/register"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Sign up here
            </Link>
          </p>
        </div>
      </div>
    </>
  )
}

export default LoginPage