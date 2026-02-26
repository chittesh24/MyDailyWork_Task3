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
      const response = await axios.post(
        `${API_URL}/api-keys/generate`,
        null,
        {
          headers: { Authorization: `Bearer ${token}` },
          params: { name: 'Default Key' }
        }
      )

      setNewApiKey(response.data.api_key)
      setApiKey(response.data.api_key)
      setShowNewKey(true)
      fetchData()
      toast.success('API key generated!')
    } catch (error) {
      console.error('Error generating API key:', error)
      toast.error('Failed to generate API key')
    }
  }

  const copyApiKey = () => {
    navigator.clipboard.writeText(newApiKey)
    toast.success('API key copied!')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <Navbar />
        <div className="container mx-auto px-4 py-16">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <Navbar />
      
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">
          Dashboard
        </h1>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <StatCard 
            title="Today's Requests"
            value={stats?.daily_requests || 0}
            icon="📊"
          />
          <StatCard 
            title="Total Requests"
            value={stats?.total_requests || 0}
            icon="🎯"
          />
          <StatCard 
            title="Active API Keys"
            value={apiKeys.filter(k => k.is_active).length}
            icon="🔑"
          />
        </div>

        {/* API Keys Section */}
        <div className="glass rounded-2xl shadow-xl p-8 mb-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              API Keys
            </h2>
            <button
              onClick={generateApiKey}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
            >
              Generate New Key
            </button>
          </div>

          {showNewKey && newApiKey && (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg p-4 mb-6">
              <p className="text-sm text-green-800 dark:text-green-200 mb-2 font-medium">
                ⚠️ Save this key now - it won't be shown again!
              </p>
              <div className="flex items-center gap-2">
                <code className="flex-1 px-3 py-2 bg-white dark:bg-gray-800 rounded border border-green-200 dark:border-green-700 text-sm font-mono">
                  {newApiKey}
                </code>
                <button
                  onClick={copyApiKey}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition"
                >
                  Copy
                </button>
              </div>
            </div>
          )}

          <div className="space-y-3">
            {apiKeys.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                No API keys yet. Generate one to get started!
              </p>
            ) : (
              apiKeys.map((key) => (
                <div 
                  key={key.id}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {key.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Created: {new Date(key.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    key.is_active 
                      ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                  }`}>
                    {key.is_active ? 'Active' : 'Revoked'}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Captions */}
        <div className="glass rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            Recent Captions
          </h2>
          <div className="space-y-3">
            {stats?.recent_captions?.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                No captions generated yet
              </p>
            ) : (
              stats?.recent_captions?.map((item: any, idx: number) => (
                <div 
                  key={idx}
                  className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
                >
                  <p className="text-gray-900 dark:text-white mb-2">
                    {item.caption}
                  </p>
                  <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                    <span>⚡ {item.inference_time_ms?.toFixed(0)}ms</span>
                    <span>{new Date(item.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon }: { title: string; value: number; icon: string }) {
  return (
    <div className="glass rounded-xl p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  )
}
