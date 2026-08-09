import React, { Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import { useLocationStore } from './stores/locationStore'

// Layout components
import Layout from './components/layout/Layout'
import AuthLayout from './components/layout/AuthLayout'

// Loading component
import LoadingSpinner from './components/ui/LoadingSpinner'

// Widgets
import CompareWidget from './components/search/CompareWidget'

// Lazy loaded pages
const HomePage = React.lazy(() => import('./pages/HomePage'))
const SearchPage = React.lazy(() => import('./pages/SearchPage'))
const ComparePage = React.lazy(() => import('./pages/ComparePage'))
const PricingPage = React.lazy(() => import('./pages/PricingPage'))
const CalculatorPage = React.lazy(() => import('./pages/CalculatorPage'))
const VerificationPage = React.lazy(() => import('./pages/VerificationPage'))
const PropertyDetailPage = React.lazy(() => import('./pages/PropertyDetailPage'))
const DashboardPage = React.lazy(() => import('./pages/DashboardPage'))
const LoginPage = React.lazy(() => import('./pages/auth/LoginPage'))
const RegisterPage = React.lazy(() => import('./pages/auth/RegisterPage'))
const ForgotPasswordPage = React.lazy(() => import('./pages/auth/ForgotPasswordPage'))
const ProfilePage = React.lazy(() => import('./pages/ProfilePage'))
const MessagesPage = React.lazy(() => import('./pages/MessagesPage'))
const AdminDashboardPage = React.lazy(() => import('./pages/admin/AdminDashboardPage'))
const NotFoundPage = React.lazy(() => import('./pages/NotFoundPage'))

// Protected route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode; roles?: string[] }> = ({ 
  children, 
  roles = [] 
}) => {
  const { user, isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <LoginPage />
  }
  
  if (roles.length > 0 && user && !roles.includes(user.role)) {
    return <NotFoundPage />
  }
  
  return <>{children}</>
}

function App() {
  const { isInitialized } = useAuthStore()
  const { requestLocation } = useLocationStore()

  // Initialize location on app start
  React.useEffect(() => {
    if (isInitialized) {
      requestLocation()
    }
  }, [isInitialized, requestLocation])

  // Show loading spinner while auth is initializing
  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="App">
      <Suspense fallback={
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <LoadingSpinner size="lg" />
        </div>
      }>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="compare" element={<ComparePage />} />
            <Route path="pricing" element={<PricingPage />} />
            <Route path="calculator" element={<CalculatorPage />} />
            <Route path="verification" element={<VerificationPage />} />
            <Route path="property/:id" element={<PropertyDetailPage />} />
          </Route>

          {/* Auth routes */}
          <Route path="/auth" element={<AuthLayout />}>
            <Route path="login" element={<LoginPage />} />
            <Route path="register" element={<RegisterPage />} />
            <Route path="forgot-password" element={<ForgotPasswordPage />} />
          </Route>

          {/* Protected routes */}
          <Route path="/app" element={<Layout />}>
            <Route path="dashboard" element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } />
            <Route path="profile" element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            } />
            <Route path="messages" element={
              <ProtectedRoute>
                <MessagesPage />
              </ProtectedRoute>
            } />
          </Route>

          {/* Admin routes */}
          <Route path="/admin" element={<Layout />}>
            <Route path="dashboard" element={
              <ProtectedRoute roles={['admin', 'super_admin']}>
                <AdminDashboardPage />
              </ProtectedRoute>
            } />
          </Route>

          {/* 404 route */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
      
      {/* Global Widgets */}
      <CompareWidget />
    </div>
  )
}

export default App