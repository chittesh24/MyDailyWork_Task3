'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import ThemeToggle from './ThemeToggle'

export default function Navbar() {
  const { isAuthenticated, logout } = useAuthStore()
  const pathname = usePathname()

  const isActive = (path: string) => pathname === path

  const NavLink = ({ href, children }: { href: string, children: React.ReactNode }) => {
    const active = isActive(href)
    return (
      <Link
        href={href}
        className={`relative px-3 py-2 text-sm font-medium transition-colors duration-300
          ${active
            ? 'text-primary-400 text-glow'
            : 'text-gray-600 dark:text-gray-300 hover:text-primary-500 dark:hover:text-primary-300 hover:text-glow'
          }
        `}
      >
        {children}
        {active && (
          <span className="absolute -bottom-1 left-0 w-full h-0.5 bg-primary-500 rounded-full shadow-[0_0_8px_rgba(99,102,241,0.6)] sm:shadow-[0_0_12px_rgba(99,102,241,0.8)] animate-pulse-subtle"></span>
        )}
      </Link>
    )
  }

  return (
    <nav className="fixed top-0 w-full z-50 glass border-b border-white/10 dark:border-white/5 transition-all duration-300">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-500 to-cyan-accent shadow-[0_0_15px_rgba(99,102,241,0.5)] group-hover:shadow-[0_0_25px_rgba(99,102,241,0.7)] transition-shadow duration-300">
              <span className="text-white font-bold text-lg relative z-10" style={{ textShadow: '0 2px 4px rgba(0,0,0,0.3)' }}>V</span>
            </div>
            <span className="text-xl font-bold tracking-tight text-gray-900 dark:text-white group-hover:text-glow transition-all duration-300">
              Vision<span className="text-primary-500 font-light">Caption</span>
            </span>
          </Link>

          {/* Navigation */}
          <div className="flex items-center space-x-2 md:space-x-6">
            {isAuthenticated ? (
              <div className="hidden md:flex items-center space-x-6 mr-4">
                <NavLink href="/dashboard">Dashboard</NavLink>
                <NavLink href="/history">History</NavLink>

                {/* User Avatar & Logout */}
                <div className="flex items-center space-x-4 pl-4 border-l border-gray-200 dark:border-white/10">
                  <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-primary-600 to-indigo-400 p-[2px] shadow-[0_0_10px_rgba(99,102,241,0.3)]">
                    <div className="h-full w-full rounded-full bg-gray-900 flex items-center justify-center">
                      <span className="text-xs text-white">ME</span>
                    </div>
                  </div>
                  <button
                    onClick={logout}
                    className="text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-red-500 transition-colors duration-300"
                  >
                    Logout
                  </button>
                </div>
              </div>
            ) : (
              <div className="hidden md:flex items-center space-x-4 mr-2">
                <NavLink href="/login">Sign In</NavLink>
                <Link
                  href="/register"
                  className="px-5 py-2 text-sm font-medium bg-white/10 dark:bg-primary-600/20 backdrop-blur-md border border-primary-500/30 text-primary-600 dark:text-primary-300 rounded-full hover:bg-primary-50 hover:dark:bg-primary-500/30 hover:shadow-[0_0_15px_rgba(99,102,241,0.4)] transition-all duration-300"
                >
                  Get Started
                </Link>
              </div>
            )}

            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
  )
}
