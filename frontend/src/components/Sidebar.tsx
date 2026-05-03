'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Home,
  BookOpen,
  DollarSign,
  User,
  BarChart3,
  MessageSquare,
  Settings,
} from 'lucide-react'

const menuItems = [
  { icon: Home, label: 'Dashboard', href: '/dashboard' },
  { icon: BookOpen, label: 'Courses', href: '/dashboard/courses' },
  { icon: DollarSign, label: 'Loans', href: '/dashboard/loans' },
  { icon: BarChart3, label: 'ROI Calculator', href: '/dashboard/roi' },
  { icon: MessageSquare, label: 'Chat', href: '/dashboard/chat' },
  { icon: User, label: 'Profile', href: '/dashboard/profile' },
  { icon: Settings, label: 'Settings', href: '/dashboard/settings' },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-neutral-900 text-white min-h-screen py-6 px-4 fixed left-0 top-16 bottom-0 overflow-y-auto hidden md:block">
      <nav className="space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/')

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                isActive
                  ? 'bg-primary-600 text-white'
                  : 'text-neutral-300 hover:bg-neutral-800'
              }`}
            >
              <Icon size={20} />
              <span className="font-medium">{item.label}</span>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
