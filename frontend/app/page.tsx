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
    <div className="relative min-h-screen overflow-hidden text-gray-900 dark:text-gray-100">
      {/* Background with animated particles (reduced on mobile) */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary-900/20 blur-[120px] animate-pulse-subtle"></div>
        <div className="absolute top-[20%] right-[-10%] w-[40%] h-[60%] rounded-full bg-cyan-900/10 blur-[150px] animate-pulse-subtle" style={{ animationDelay: '2s' }}></div>
        {/* Particles (visible mostly on md+) */}
        <div className="hidden md:block absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4IiBoZWlnaHQ9IjgiPgo8cmVjdCB3aWR0aD0iOCIgaGVpZ2h0PSI4IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDIiLz4KPC9zdmc+')] opacity-50 z-0"></div>
      </div>

      <Navbar />

      {/* Hero Section */}
      <section className="relative container mx-auto px-4 pt-32 pb-24 z-10">
        <div className="text-center mb-16 animate-slide-up max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-button text-xs font-semibold text-primary-400 mb-6 border border-primary-500/30">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
            </span>
            VisionCaption AI 2.0 is live
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-white via-indigo-200 to-cyan-200 mb-6 drop-shadow-lg leading-tight">
            Generate Intelligent <br className="hidden md:block" /> Image Captions with AI
          </h1>
          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed mb-10">
            Advanced CNN + Transformer architecture. Instantly generate highly accurate, contextual descriptions for any image.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button className="relative group px-8 py-4 rounded-xl font-bold text-white bg-primary-600 hover:bg-primary-500 transition-all duration-300 w-full sm:w-auto shadow-[0_0_20px_rgba(99,102,241,0.4)] hover:shadow-[0_0_30px_rgba(99,102,241,0.6)]">
              <div className="absolute inset-0 w-full h-full rounded-xl -z-10 group-hover:animate-pulse-glow glow-border"></div>
              Get Started Free
            </button>
            <button className="px-8 py-4 rounded-xl font-bold text-white glass-button w-full sm:w-auto hover:text-cyan-accent group transition-all duration-300">
              View API Documentation
            </button>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 animate-bounce-soft hidden sm:flex flex-col items-center">
          <span className="text-xs text-gray-500 mb-2 uppercase tracking-widest font-semibold">Scroll</span>
          <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
        </div>
      </section>

      {/* Main App Demo Content */}
      <section className="relative z-20 pb-24 px-4 sm:px-6">
        <div className="max-w-4xl mx-auto animate-slide-up" style={{ animationDelay: '0.2s' }}>
          {/* Demo mode container with depth separation */}
          <div className="glass-panel rounded-3xl p-2 sm:p-6 md:p-10 relative">
            {/* Subtle inner reflection */}
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>

            <div className="space-y-8 relative z-10 bg-[#0B0F19]/60 dark:bg-[#111827]/60 rounded-2xl p-4 sm:p-8 border border-white/5">
              <ImageUploader
                onCaptionGenerated={handleCaptionGenerated}
                onUploadStart={handleUploadStart}
              />

              {isLoading && (
                <div className="glass rounded-2xl p-8 relative overflow-hidden flex flex-col items-center justify-center space-y-4">
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary-500/10 to-transparent animate-[shimmer_2s_infinite]"></div>
                  <div className="relative w-16 h-16 pointer-events-none">
                    <svg className="animate-spin text-primary-500" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <circle cx="12" cy="12" r="10" strokeWidth="2" strokeOpacity="0.2"></circle>
                      <path d="M12 2a10 10 0 0 1 10 10" strokeWidth="2" strokeLinecap="round"></path>
                    </svg>
                  </div>
                  <span className="text-gray-300 font-medium tracking-wide">AI is analyzing your image...</span>
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
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 py-24 bg-gray-900/40 border-y border-white/5">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">Enterprise-Grade Architecture</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">Built for scale, speed, and accuracy.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6 lg:gap-8 max-w-6xl mx-auto">
            <FeatureCard
              icon={<svg className="w-8 h-8 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>}
              title="Advanced AI Model"
              description="Hybrid ResNet50 encoder and Transformer decoder trained on millions of parameters."
              colorClass="from-primary-500/20 to-indigo-500/20"
            />
            <FeatureCard
              icon={<svg className="w-8 h-8 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>}
              title="Sub-second Inference"
              description="Optimized pipeline with beam search and mixed precision support for real-time results."
              colorClass="from-cyan-500/20 to-blue-500/20"
            />
            <FeatureCard
              icon={<svg className="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>}
              title="Secure API Infrastructure"
              description="JWT authentication, intelligent rate limiting, and fully encrypted API key management."
              colorClass="from-emerald-500/20 to-green-500/20"
            />
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="relative z-10 py-24 pb-32">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">Simple, transparent pricing</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">Start building with VisionCaption AI today.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <PricingCard
              title="Developer"
              price="Free"
              features={['100 requests / day', 'Standard support', 'REST API Access', 'Shared infrastructure']}
              buttonText="Start Free Trial"
            />
            <PricingCard
              title="Pro"
              price="$49"
              period="/mo"
              features={['10,000 requests / day', 'Priority support', 'Webhooks', 'Dedicated inference node']}
              buttonText="Upgrade to Pro"
              highlight=true
            />
          </div>
        </div>
      </section>

      {/* Footer minimal glass strip */}
      <footer className="relative z-10 glass border-t border-white/10 dark:border-white/5 py-8 opacity-80 backdrop-blur-md">
        <div className="container mx-auto px-4 flex flex-col md:flex-row justify-between items-center text-sm text-gray-500">
          <div>© 2026 VisionCaption AI. All rights reserved.</div>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <span className="hover:text-white cursor-pointer transition">Privacy</span>
            <span className="hover:text-white cursor-pointer transition">Terms</span>
            <span className="hover:text-white cursor-pointer transition">API Docs</span>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description, colorClass }: { icon: React.ReactNode; title: string; description: string; colorClass: string }) {
  return (
    <div className="group glass rounded-2xl p-8 hover:-translate-y-2 hover:shadow-[0_10px_40px_-10px_rgba(99,102,241,0.3)] transition-all duration-300 relative overflow-hidden border border-white/5 hover:border-white/10">
      <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl ${colorClass} blur-[50px] opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>
      <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mb-6 shadow-inner group-hover:scale-110 transition-transform duration-300 ease-out border border-white/10">
        {icon}
      </div>
      <h3 className="text-2xl font-bold text-gray-100 mb-3 tracking-wide">{title}</h3>
      <p className="text-gray-400 leading-relaxed text-sm">{description}</p>
    </div>
  )
}

function PricingCard({ title, price, period, features, buttonText, highlight }: { title: string; price: string; period?: string; features: string[]; buttonText: string; highlight?: boolean }) {
  return (
    <div className={`glass rounded-3xl p-8 transition-all duration-300 relative overflow-hidden group hover:-translate-y-2 ${highlight ? 'border-primary-500/50 shadow-[0_0_30px_rgba(99,102,241,0.15)] hover:shadow-[0_10px_40px_rgba(99,102,241,0.3)]' : 'border-white/10 hover:shadow-cyan-500/10 hover:border-white/20'}`}>
      {highlight && <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary-400 to-cyan-400"></div>}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-400 mb-2">{title}</h3>
        <div className="flex items-baseline gap-1">
          <span className="text-5xl font-extrabold text-white tracking-tight">{price}</span>
          {period && <span className="text-gray-500">{period}</span>}
        </div>
      </div>
      <ul className="space-y-4 mb-8">
        {features.map((feature, idx) => (
          <li key={idx} className="flex items-center gap-3 text-gray-300">
            <svg className={`w-5 h-5 ${highlight ? 'text-primary-400' : 'text-gray-500'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
            {feature}
          </li>
        ))}
      </ul>
      <button className={`w-full py-4 rounded-xl font-bold transition-all duration-300 ${highlight ? 'bg-primary-600 hover:bg-primary-500 text-white shadow-[0_4px_14px_0_rgba(99,102,241,0.39)] hover:shadow-[0_6px_20px_rgba(99,102,241,0.23)] hover:-translate-y-0.5' : 'glass-button text-gray-200 hover:text-white'}`}>
        {buttonText}
      </button>
    </div>
  )
}
