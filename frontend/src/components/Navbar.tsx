'use client'

import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { Menu, X, LogOut, User } from 'lucide-react'

export default function Navbar() {
  const router = useRouter()
  const { user, logout } = useAuth()
  const [isOpen, setIsOpen] = React.useState(false)

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-neutral-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">✓</span>
            </div>
            <span className="font-bold text-lg text-neutral-900 hidden sm:inline">StudePath</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-6">
            <Link href="/dashboard" className="text-neutral-700 hover:text-primary-600 transition">
              Dashboard
            </Link>
            <Link href="/dashboard/courses" className="text-neutral-700 hover:text-primary-600 transition">
              Courses
            </Link>
            <Link href="/dashboard/loans" className="text-neutral-700 hover:text-primary-600 transition">
              Loans
            </Link>
            <Link href="/dashboard/profile" className="text-neutral-700 hover:text-primary-600 transition">
              Profile
            </Link>
          </div>

          {/* Profile & Mobile Menu */}
          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-3">
              <div className="text-right">
                <p className="text-sm font-medium text-neutral-900">{user?.first_name}</p>
                <p className="text-xs text-neutral-500">{user?.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 hover:bg-neutral-100 rounded-lg transition"
                title="Logout"
              >
                <LogOut size={20} className="text-neutral-600" />
              </button>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="md:hidden p-2 hover:bg-neutral-100 rounded-lg"
            >
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden pb-4 space-y-2 border-t border-neutral-200">
            <Link href="/dashboard" className="block px-4 py-2 text-neutral-700 hover:bg-neutral-100 rounded">
              Dashboard
            </Link>
            <Link href="/dashboard/courses" className="block px-4 py-2 text-neutral-700 hover:bg-neutral-100 rounded">
              Courses
            </Link>
            <Link href="/dashboard/loans" className="block px-4 py-2 text-neutral-700 hover:bg-neutral-100 rounded">
              Loans
            </Link>
            <Link href="/dashboard/profile" className="block px-4 py-2 text-neutral-700 hover:bg-neutral-100 rounded">
              Profile
            </Link>
            <button
              onClick={handleLogout}
              className="w-full text-left px-4 py-2 text-danger hover:bg-neutral-100 rounded flex items-center gap-2"
            >
              <LogOut size={18} /> Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}
