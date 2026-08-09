import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

const MobileNavigation: React.FC = () => {
  const location = useLocation()
  const { isAuthenticated } = useAuthStore()

  const navItems = isAuthenticated
    ? [
        { path: '/', label: 'Home', icon: '🏠' },
        { path: '/search', label: 'Search', icon: '🔍' },
        { path: '/app/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/app/messages', label: 'Messages', icon: '💬' },
      ]
    : [
        { path: '/', label: 'Home', icon: '🏠' },
        { path: '/search', label: 'Search', icon: '🔍' },
        { path: '/auth/login', label: 'Login', icon: '👤' },
        { path: '/auth/register', label: 'Sign Up', icon: '📝' },
      ]

  return (
    <nav className="bottom-nav">
      {navItems.map((item) => {
        const isActive = location.pathname === item.path
        return (
          <Link
            key={item.path}
            to={item.path}
            className={
              isActive ? 'bottom-nav-item-active' : 'bottom-nav-item-inactive'
            }
          >
            <span className="text-lg">{item.icon}</span>
            <span className="mt-1">{item.label}</span>
          </Link>
        )
      })}
    </nav>
  )
}

export default MobileNavigation