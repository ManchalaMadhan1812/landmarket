// PWA Service Worker registration and utilities

export const registerSW = () => {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', async () => {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js', {
          scope: '/'
        })
        
        console.log('SW registered: ', registration)
        
        // Handle updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed') {
                if (navigator.serviceWorker.controller) {
                  // New content is available, inform the user
                  showUpdateAvailable()
                } else {
                  // Content is cached for the first time
                  console.log('Content is cached for offline use')
                }
              }
            })
          }
        })
      } catch (error) {
        console.log('SW registration failed: ', error)
      }
    })
  }
}

export const showUpdateAvailable = () => {
  // Show a user-friendly notification about the update
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification('App Update Available', {
      body: 'A new version of LandMarket is available. Refresh to update.',
      icon: '/pwa-192x192.png'
    })
  }
  
  // You can also show an in-app banner or modal here
  console.log('App update available')
}

export const requestNotificationPermission = async () => {
  if ('Notification' in window) {
    const permission = await Notification.requestPermission()
    return permission === 'granted'
  }
  return false
}

export const isStandalone = () => {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    (window.navigator as any).standalone ||
    document.referrer.includes('android-app://')
  )
}

export const canInstallPWA = () => {
  return 'beforeinstallprompt' in window
}

export const getInstallPrompt = () => {
  return (window as any).deferredPrompt
}

export const setInstallPrompt = (prompt: any) => {
  ;(window as any).deferredPrompt = prompt
}

// Handle PWA installation
export const handleInstallPrompt = () => {
  window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent the mini-infobar from appearing on mobile
    e.preventDefault()
    // Stash the event so it can be triggered later
    setInstallPrompt(e)
    
    // Show your custom install button
    showInstallButton()
  })

  window.addEventListener('appinstalled', () => {
    // Hide the app-provided install promotion
    hideInstallButton()
    // Clear the deferredPrompt so it can be garbage collected
    setInstallPrompt(null)
    
    console.log('PWA was installed')
  })
}

const showInstallButton = () => {
  // Implement your custom install button display logic
  const installButton = document.getElementById('install-button')
  if (installButton) {
    installButton.style.display = 'block'
  }
}

const hideInstallButton = () => {
  // Implement your custom install button hide logic
  const installButton = document.getElementById('install-button')
  if (installButton) {
    installButton.style.display = 'none'
  }
}

export const installPWA = async () => {
  const deferredPrompt = getInstallPrompt()
  
  if (deferredPrompt) {
    // Show the install prompt
    deferredPrompt.prompt()
    
    // Wait for the user to respond to the prompt
    const { outcome } = await deferredPrompt.userChoice
    
    // Clear the deferredPrompt
    setInstallPrompt(null)
    
    return outcome === 'accepted'
  }
  
  return false
}

// Initialize PWA features
export const initializePWA = () => {
  registerSW()
  handleInstallPrompt()
  
  // Request notification permission after user interaction
  document.addEventListener('click', () => {
    requestNotificationPermission()
  }, { once: true })
}