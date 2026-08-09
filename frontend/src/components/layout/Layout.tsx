import React from 'react'
import { Outlet } from 'react-router-dom'
import Header from './Header'
import Footer from './Footer'
import MobileNavigation from './MobileNavigation'

const Layout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      
      <main className="flex-1 pb-16 md:pb-0">
        <Outlet />
      </main>
      
      <Footer />
      
      {/* Mobile bottom navigation */}
      <div className="md:hidden">
        <MobileNavigation />
      </div>
    </div>
  )
}

export default Layout