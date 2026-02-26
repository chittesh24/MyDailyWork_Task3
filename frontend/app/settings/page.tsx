'use client'

import { useState } from 'react'
import Navbar from '@/components/Navbar'
import { useAuthStore } from '@/store/authStore'
import { useRouter } from 'next/navigation'

export default function SettingsPage() {
  const { isAuthenticated, user } = useAuthStore()
  const router = useRouter()
  const [theme, setTheme] = useState('blue')
  const [fontSize, setFontSize] = useState('medium')
  const [animations, setAnimations] = useState(true)

  if (!isAuthenticated) {
    router.push('/login')
    return null
  }

  const themes = [
    { id: 'blue', name: 'Ocean Blue', primary: '#0ea5e9', secondary: '#38bdf8' },
    { id: 'purple', name: 'Royal Purple', primary: '#a855f7', secondary: '#c084fc' },
    { id: 'green', name: 'Forest Green', primary: '#10b981', secondary: '#34d399' },
    { id: 'orange', name: 'Sunset Orange', primary: '#f97316', secondary: '#fb923c' },
    { id: 'pink', name: 'Cherry Blossom', primary: '#ec4899', secondary: '#f472b6' },
    { id: 'teal', name: 'Ocean Teal', primary: '#14b8a6', secondary: '#2dd4bf' },
  ]

  const handleSaveSettings = () => {
    localStorage.setItem('app-theme', theme)
    localStorage.setItem('app-fontSize', fontSize)
    localStorage.setItem('app-animations', animations.toString())
    
    // Apply theme
    document.documentElement.style.setProperty('--primary-color', themes.find(t => t.id === theme)?.primary || '#0ea5e9')
    
    alert('Settings saved!')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <Navbar />
      
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">
          Settings
        </h1>

        <div className="max-w-4xl">
          {/* Account Settings */}
          <div className="glass rounded-2xl shadow-xl p-8 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              Account
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={user?.email || ''}
                  disabled
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
          </div>

          {/* Appearance Settings */}
          <div className="glass rounded-2xl shadow-xl p-8 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              Appearance
            </h2>

            {/* Theme Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Color Theme
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {themes.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setTheme(t.id)}
                    className={`
                      p-4 rounded-lg border-2 transition-all
                      ${theme === t.id 
                        ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20' 
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                      }
                    `}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <div
                        className="w-8 h-8 rounded-full"
                        style={{ backgroundColor: t.primary }}
                      />
                      <div
                        className="w-8 h-8 rounded-full"
                        style={{ backgroundColor: t.secondary }}
                      />
                    </div>
                    <p className="font-medium text-gray-900 dark:text-white">{t.name}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Font Size */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Font Size
              </label>
              <div className="flex gap-3">
                {['small', 'medium', 'large'].map((size) => (
                  <button
                    key={size}
                    onClick={() => setFontSize(size)}
                    className={`
                      px-6 py-3 rounded-lg font-medium transition-all
                      ${fontSize === size
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300'
                      }
                    `}
                  >
                    {size.charAt(0).toUpperCase() + size.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Animations Toggle */}
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white">
                  Enable Animations
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Smooth transitions and effects
                </p>
              </div>
              <button
                onClick={() => setAnimations(!animations)}
                className={`
                  relative w-14 h-7 rounded-full transition-colors
                  ${animations ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'}
                `}
              >
                <div className={`
                  absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full transition-transform
                  ${animations ? 'translate-x-7' : 'translate-x-0'}
                `} />
              </button>
            </div>
          </div>

          {/* Preferences */}
          <div className="glass rounded-2xl shadow-xl p-8 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              Preferences
            </h2>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="block text-sm font-medium text-gray-900 dark:text-white">
                    Auto-save Captions
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Automatically save generated captions
                  </p>
                </div>
                <input type="checkbox" className="w-5 h-5 text-primary-600" defaultChecked />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="block text-sm font-medium text-gray-900 dark:text-white">
                    Show Inference Time
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Display generation time in results
                  </p>
                </div>
                <input type="checkbox" className="w-5 h-5 text-primary-600" defaultChecked />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="block text-sm font-medium text-gray-900 dark:text-white">
                    Email Notifications
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Receive updates and announcements
                  </p>
                </div>
                <input type="checkbox" className="w-5 h-5 text-primary-600" />
              </div>
            </div>
          </div>

          {/* Save Button */}
          <button
            onClick={handleSaveSettings}
            className="w-full px-6 py-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition font-medium text-lg"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  )
}
