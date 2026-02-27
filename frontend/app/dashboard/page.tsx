'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/store/authStore'
import Navbar from '@/components/Navbar'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function DashboardPage() {
  const { isAuthenticated, token, apiKey, setApiKey } = useAuthStore()
  const [stats, setStats] = useState<any>(null)
  const [apiKeys, setApiKeys] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showNewKey, setShowNewKey] = useState(false)
  const [newApiKey, setNewApiKey] = useState('')
  const router = useRouter()

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    fetchData()
  }, [isAuthenticated, router])

  const fetchData = async () => {
    try {
      const [statsRes, keysRes] = await Promise.all([
        axios.get(`${API_URL}/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api-keys/list`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ])

      setStats(statsRes.data)
      setApiKeys(keysRes.data)
    } catch (error) {
      console.error('Error fetching data:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setIsLoading(false)
    }
  }

  const generateApiKey = async () => {
    try {
      // Adding a toast promise could make this feel more premium
      const generateReq = axios.post(
        `${API_URL}/api-keys/generate`,
        null,
        {
          headers: { Authorization: `Bearer ${token}` },
          params: { name: 'Vision Key ' + (apiKeys.length + 1) }
        }
      )

      toast.promise(generateReq, {
        loading: 'Generating secure key...',
        success: 'API Key Generated',
        error: 'Failed to generate key'
      })

      const response = await generateReq

      setNewApiKey(response.data.api_key)
      setApiKey(response.data.api_key)
      setShowNewKey(true)
      fetchData()
    } catch (error) {
      console.error('Error generating API key:', error)
    }
  }

  const copyApiKey = (keyToCopy: string) => {
    navigator.clipboard.writeText(keyToCopy)
    toast.success('Key copied to clipboard!', { icon: '📋' })
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0B0F19] relative overflow-hidden flex flex-col">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-[#0B0F19] to-black -z-20"></div>
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-lg h-[500px] bg-primary-600/20 rounded-full blur-[120px] -z-10 mix-blend-screen pointer-events-none"></div>

        <Navbar />
        <div className="flex-1 container mx-auto px-4 py-16 flex justify-center items-center">
          <div className="relative w-16 h-16">
            <div className="absolute inset-0 rounded-full border-t-2 border-primary-500 animate-spin"></div>
            <div className="absolute inset-2 rounded-full border-r-2 border-cyan-400 animate-spin-slow"></div>
            <div className="absolute inset-4 rounded-full border-b-2 border-white/20 animate-spin"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0B0F19] relative overflow-hidden text-gray-300">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-[#0B0F19] to-black -z-20"></div>
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-600/10 rounded-full blur-[120px] -z-10 pointer-events-none mix-blend-screen"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-cyan-600/10 rounded-full blur-[120px] -z-10 pointer-events-none mix-blend-screen"></div>

      <Navbar />

      <main className="container mx-auto px-4 py-24 sm:py-32 relative z-10 max-w-6xl">
        <header className="mb-12">
          <h1 className="text-4xl sm:text-5xl font-bold text-white tracking-tight mb-4 drop-shadow-sm">
            Command Center
          </h1>
          <p className="text-gray-400 text-lg">Monitor your usage and manage API configurations.</p>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          <StatCard
            title="Today's Requests"
            value={stats?.daily_requests || 0}
            icon={
              <svg className="w-8 h-8 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            }
          />
          <StatCard
            title="Total Requests"
            value={stats?.total_requests || 0}
            icon={
              <svg className="w-8 h-8 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
              </svg>
            }
          />
          <StatCard
            title="Active API Keys"
            value={apiKeys.filter(k => k.is_active).length}
            icon={
              <svg className="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
            }
          />
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* API Keys Section (Spans 2 columns) */}
          <div className="lg:col-span-2 space-y-8">
            <div className="glass-panel p-8 rounded-2xl">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8 border-b border-white/10 pb-6">
                <div>
                  <h2 className="text-2xl font-bold text-white tracking-tight">
                    API Keys
                  </h2>
                  <p className="text-sm text-gray-400 mt-1">Manage keys for programmatic access to VisionCaption AI.</p>
                </div>
                <button
                  onClick={generateApiKey}
                  className="glass-button px-5 py-2.5 rounded-xl text-sm font-semibold text-white group flex items-center gap-2"
                >
                  <span className="text-primary-400 group-hover:animate-spin-slow">✦</span>
                  Generate New Key
                </button>
              </div>

              {showNewKey && newApiKey && (
                <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-5 mb-8 animate-fade-in relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/20 rounded-full blur-3xl -z-10 mix-blend-screen pointer-events-none"></div>
                  <p className="text-sm text-emerald-300 mb-3 font-medium flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    Save this key now - it won't be shown again!
                  </p>
                  <div className="flex items-center gap-3">
                    <code className="flex-1 px-4 py-3 bg-[#0B0F19]/80 backdrop-blur-md rounded-lg border border-emerald-500/20 text-sm font-mono text-white tracking-wider break-all">
                      {newApiKey}
                    </code>
                    <button
                      onClick={() => copyApiKey(newApiKey)}
                      className="px-4 py-3 bg-emerald-500/20 text-emerald-300 hover:text-white rounded-lg hover:bg-emerald-500/40 transition-colors border border-emerald-500/30 font-medium"
                    >
                      Copy
                    </button>
                  </div>
                </div>
              )}

              <div className="space-y-4">
                {apiKeys.length === 0 ? (
                  <div className="text-center py-12 px-4 rounded-xl border border-dashed border-white/10 bg-white/5">
                    <p className="text-gray-400 mb-2">No API keys generated yet.</p>
                    <p className="text-sm text-gray-500">Create one to start integrating VisionCaption into your apps.</p>
                  </div>
                ) : (
                  <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="border-b border-white/10 bg-white/5">
                          <th className="py-4 px-6 text-sm font-semibold text-gray-300">Name</th>
                          <th className="py-4 px-6 text-sm font-semibold text-gray-300">Created</th>
                          <th className="py-4 px-6 text-sm font-semibold text-gray-300">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {apiKeys.map((key) => (
                          <tr key={key.id} className="border-b border-white/5 hover:bg-white/5 transition-colors group">
                            <td className="py-4 px-6">
                              <p className="font-medium text-white group-hover:text-primary-300 transition-colors">
                                {key.name}
                              </p>
                            </td>
                            <td className="py-4 px-6 text-sm text-gray-400">
                              {new Date(key.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                            </td>
                            <td className="py-4 px-6">
                              <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${key.is_active
                                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]'
                                  : 'bg-gray-800 text-gray-400 border-gray-700'
                                }`}>
                                {key.is_active && <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>}
                                {key.is_active ? 'Active' : 'Revoked'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Recent Captions Section (Spans 1 column) */}
          <div className="glass-panel p-8 rounded-2xl h-fit">
            <h2 className="text-xl font-bold text-white tracking-tight mb-6 pb-4 border-b border-white/10">
              Recent Activity
            </h2>
            <div className="space-y-4">
              {stats?.recent_captions?.length === 0 ? (
                <p className="text-gray-500 text-sm text-center py-8">
                  No captions generated yet.
                </p>
              ) : (
                stats?.recent_captions?.map((item: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-4 bg-white/5 hover:bg-white/10 border border-white/5 rounded-xl transition-all duration-300 cursor-default group relative overflow-hidden"
                  >
                    <div className="absolute inset-0 bg-gradient-to-tr from-primary-500/0 to-cyan-500/0 group-hover:from-primary-500/5 group-hover:to-cyan-500/5 transition-colors"></div>
                    <p className="text-sm text-gray-200 mb-3 line-clamp-2 relative z-10 leading-relaxed font-medium">
                      "{item.caption}"
                    </p>
                    <div className="flex items-center justify-between text-xs font-medium text-gray-500 group-hover:text-gray-400 relative z-10">
                      <span className="flex items-center gap-1">
                        <span className="text-cyan-400">⚡</span>
                        {item.inference_time_ms?.toFixed(0)}ms
                      </span>
                      <span>
                        {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function StatCard({ title, value, icon }: { title: string; value: number | string; icon: React.ReactNode }) {
  return (
    <div className="glass-panel rounded-2xl p-6 relative overflow-hidden group">
      {/* Background glow effect on hover */}
      <div className="absolute -inset-px bg-gradient-to-b from-primary-500/0 to-primary-500/0 group-hover:from-primary-500/10 group-hover:to-transparent rounded-2xl transition-all duration-500 pointer-events-none"></div>

      <div className="flex items-start justify-between relative z-10">
        <div className="space-y-2">
          <p className="text-gray-400 text-sm font-medium tracking-wide uppercase">{title}</p>
          <p className="text-4xl font-bold text-white tracking-tight text-glow">
            {value}
          </p>
        </div>
        <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:scale-110 group-hover:bg-white/10 transition-all duration-300 shadow-[0_0_15px_rgba(0,0,0,0.5)]">
          {icon}
        </div>
      </div>
    </div>
  )
}
