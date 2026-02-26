'use client'

import { useState } from 'react'
import Link from 'next/link'
import Navbar from '@/components/Navbar'
import ImageUploader from '@/components/ImageUploader'
import CaptionResult from '@/components/CaptionResult'
import { useAuthStore } from '@/store/authStore'

export default function Home() {
  const { isAuthenticated } = useAuthStore()
  const [caption, setCaption] = useState<string | null>(null)
  const [inferenceTime, setInferenceTime] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleCaptionGenerated = (data: { caption: string; inference_time_ms: number }) => {
    setCaption(data.caption)
    setInferenceTime(data.inference_time_ms)
    setIsLoading(false)
  }

  const handleUploadStart = () => {
    setIsLoading(true)
    setCaption(null)
    setInferenceTime(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <Navbar />
      
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-4">
            Image Captioning AI
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Advanced CNN + Transformer architecture for production-grade image captioning
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {/* Demo mode - no authentication required */}
          <div className="space-y-8">
            <ImageUploader 
              onCaptionGenerated={handleCaptionGenerated}
              onUploadStart={handleUploadStart}
            />
            
            {isLoading && (
              <div className="glass rounded-2xl shadow-xl p-8">
                <div className="flex items-center justify-center space-x-3">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                  <span className="text-gray-700 dark:text-gray-300">Generating caption...</span>
                </div>
              </div>
            )}
            
            {caption && !isLoading && (
              <CaptionResult 
                caption={caption}
                inferenceTime={inferenceTime}
              />
            )}
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-24 grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <FeatureCard 
            icon="🧠"
            title="Advanced AI"
            description="ResNet50 encoder with Transformer decoder for state-of-the-art results"
          />
          <FeatureCard 
            icon="⚡"
            title="Fast Inference"
            description="Optimized pipeline with beam search and mixed precision support"
          />
          <FeatureCard 
            icon="🔒"
            title="Secure API"
            description="JWT authentication, rate limiting, and encrypted API keys"
          />
        </div>
      </section>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="glass rounded-xl p-6 text-center hover:shadow-xl transition-shadow">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">{title}</h3>
      <p className="text-gray-600 dark:text-gray-300">{description}</p>
    </div>
  )
}
