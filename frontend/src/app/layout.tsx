'use client'

import React, { ReactNode } from 'react'
import Navbar from '@/components/Navbar'
import Sidebar from '@/components/Sidebar'
import { useAuth } from '@/hooks/useAuth'
import { useRouter, usePathname } from 'next/navigation'

interface RootLayoutProps {
  children: ReactNode
}

const publicRoutes = ['/', '/login', '/signup', '/demo']

export default function RootLayout({ children }: RootLayoutProps) {
  const pathname = usePathname()
  const router = useRouter()
  const { isAuthenticated, user } = useAuth()
  const [hydrated, setHydrated] = React.useState(false)

  React.useEffect(() => {
    setHydrated(true)
  }, [])

  if (!hydrated) return null

  // Check if user should be authenticated
  const isPublicRoute = publicRoutes.includes(pathname)
  const shouldRedirect = !isPublicRoute && !isAuthenticated

  if (shouldRedirect) {
    router.push('/login')
    return null
  }

  const isDashboard = pathname.startsWith('/dashboard')

  return (
    <html lang="en">
      <head>
        <title>Unified Student Platform</title>
        <meta name="description" content="AI-powered student engagement and education financing" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="bg-neutral-50">
        {!isPublicRoute && <Navbar />}
        <div className={isDashboard ? 'flex' : ''}>
          {isDashboard && <Sidebar />}
          <main className={isDashboard ? 'flex-1' : 'w-full'}>
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
