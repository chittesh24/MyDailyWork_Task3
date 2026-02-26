'use client'

import Link from 'next/link'
import { useAuthStore } from '@/store/authStore'
import ThemeToggle from './ThemeToggle'

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore()

  return (
    <nav className="glass border-b border-gray-200 dark:border-gray-700">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-primary-600">🎨</span>
            <span className="text-xl font-bold text-gray-900 dark:text-white">
              ImageCaption AI
            </span>
          </Link>

          {/* Navigation */}
          <div className="flex items-center space-x-6">
            {isAuthenticated ? (
              <>
                <Link 
                  href="/dashboard"
                  className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition"
                >
                  Dashboard
                </Link>
                <Link 
                  href="/history"
                  className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition"
                >
                  History
                </Link>
                <button
                  onClick={logout}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link 
                  href="/login"
                  className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition"
                >
                  Sign In
                </Link>
                <Link 
                  href="/register"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                >
                  Get Started
                </Link>
              </>
            )}
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
  )
}
