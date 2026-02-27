'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import axios from 'axios'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/store/authStore'
import Navbar from '@/components/Navbar'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { login } = useAuthStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (password !== confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    if (password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }

    setIsLoading(true)

    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        email,
        password,
      })

      login(response.data.access_token, email)
      toast.success('Registration successful!')
      router.push('/dashboard')
    } catch (error: any) {
      console.error('Registration error:', error)
      const message = error.response?.data?.detail || 'Registration failed'
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0B0F19] relative overflow-hidden flex flex-col">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-[#0B0F19] to-black -z-20"></div>
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-full max-w-lg h-[400px] bg-cyan-600/10 rounded-full blur-[120px] -z-10 mix-blend-screen pointer-events-none"></div>

      <Navbar />

      <div className="flex-1 flex items-center justify-center p-4 py-20 relative z-10">
        <div className="w-full max-w-md animate-slide-up">
          <div className="glass-panel rounded-2xl p-8 sm:p-10 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
            <div className="mb-8 text-center">
              <div className="inline-flex justify-center items-center w-16 h-16 rounded-2xl bg-white/5 border border-white/10 mb-4 shadow-[inset_0_0_20px_rgba(255,255,255,0.05)]">
                <span className="text-3xl">🚀</span>
              </div>
              <h1 className="text-3xl font-bold tracking-tight text-white mb-2 text-glow">
                Create Account
              </h1>
              <p className="text-gray-400">Join VisionCaption AI today</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-300">
                  Email Address
                </label>
                <div className="relative group/input">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoComplete="email"
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-gray-500 focus:outline-none focus:border-primary-400 focus:ring-1 focus:ring-primary-400/50 transition-all duration-300"
                    placeholder="you@example.com"
                  />
                  <div className="absolute inset-0 -z-10 bg-primary-500/0 group-focus-within/input:bg-primary-500/10 rounded-xl blur-md transition-all duration-300"></div>
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-300">
                  Password
                </label>
                <div className="relative group/input">
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={8}
                    autoComplete="new-password"
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-gray-500 focus:outline-none focus:border-primary-400 focus:ring-1 focus:ring-primary-400/50 transition-all duration-300"
                    placeholder="••••••••"
                  />
                  <div className="absolute inset-0 -z-10 bg-primary-500/0 group-focus-within/input:bg-primary-500/10 rounded-xl blur-md transition-all duration-300"></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">Must be at least 8 characters.</p>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-300">
                  Confirm Password
                </label>
                <div className="relative group/input">
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    minLength={8}
                    autoComplete="new-password"
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-gray-500 focus:outline-none focus:border-primary-400 focus:ring-1 focus:ring-primary-400/50 transition-all duration-300"
                    placeholder="••••••••"
                  />
                  <div className="absolute inset-0 -z-10 bg-primary-500/0 group-focus-within/input:bg-primary-500/10 rounded-xl blur-md transition-all duration-300"></div>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full mt-8 relative group overflow-hidden rounded-xl bg-white/10 p-px font-semibold text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                <span className="absolute inset-0 bg-gradient-to-r from-cyan-500/50 via-primary-500/50 to-cyan-500/50 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></span>
                <div className="relative flex h-full w-full items-center justify-center gap-2 rounded-xl bg-[#0B0F19] px-6 py-3 transition-colors group-hover:bg-opacity-0">
                  {isLoading ? (
                    <>
                      <svg className="w-5 h-5 animate-spin text-cyan-400" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Creating Account...
                    </>
                  ) : (
                    'Create Account →'
                  )}
                </div>
              </button>
            </form>

            <p className="mt-8 text-center text-sm text-gray-500">
              Already have an account?{' '}
              <Link href="/login" className="font-medium text-cyan-400 hover:text-cyan-300 tracking-wide transition-colors">
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
