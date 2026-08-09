import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'

const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // TODO: Implement actual forgot password API call
      setTimeout(() => {
        setIsLoading(false)
        setIsSubmitted(true)
      }, 1000)
    } catch (error) {
      setIsLoading(false)
      console.error('Forgot password error:', error)
    }
  }

  if (isSubmitted) {
    return (
      <>
        <Helmet>
          <title>Check Your Email - LandMarket</title>
        </Helmet>

        <div className="text-center space-y-6">
          <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto">
            <span className="text-2xl">✉️</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Check Your Email</h2>
          <p className="text-gray-600">
            We've sent a password reset link to{' '}
            <span className="font-medium">{email}</span>
          </p>
          <div className="space-y-4">
            <p className="text-sm text-gray-500">
              Didn't receive the email? Check your spam folder or try again.
            </p>
            <Link
              to="/auth/login"
              className="btn-primary w-full"
            >
              Back to Login
            </Link>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <Helmet>
        <title>Forgot Password - LandMarket</title>
      </Helmet>

      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Forgot Password?</h2>
          <p className="text-gray-600 mt-2">
            Enter your email address and we'll send you a reset link
          </p>
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

          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary w-full"
          >
            {isLoading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>

        <div className="text-center">
          <Link
            to="/auth/login"
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            ← Back to Login
          </Link>
        </div>
      </div>
    </>
  )
}

export default ForgotPasswordPage