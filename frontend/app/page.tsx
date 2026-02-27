'use client'

import { useState, useCallback, useEffect, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import toast, { Toaster } from 'react-hot-toast'
import Navbar from '@/components/Navbar'
import CaptionResult from '@/components/CaptionResult'

// Dynamically import transformers only in browser
let transformersPipeline: any = null

export default function Home() {
  const [captioner, setCaptioner] = useState<any>(null)
  const [isLoadingModel, setIsLoadingModel] = useState(false)
  const [loadingProgress, setLoadingProgress] = useState(0)
  const [loadingMessage, setLoadingMessage] = useState('')
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [caption, setCaption] = useState<string | null>(null)
  const [inferenceTime, setInferenceTime] = useState<number | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const demoRef = useRef<HTMLDivElement>(null)

  // Load transformers.js dynamically (browser only)
  useEffect(() => {
    const loadTransformers = async () => {
      try {
        const transformers = await import('@xenova/transformers')
        transformersPipeline = transformers.pipeline
        const env = transformers.env
        env.allowLocalModels = false
        env.useBrowserCache = true
        env.allowRemoteModels = true
        console.log('✅ Transformers.js loaded')
      } catch (error) {
        console.error('Failed to load Transformers.js:', error)
      }
    }
    loadTransformers()
  }, [])

  // Load AI model
  const loadModel = async () => {
    if (!transformersPipeline) {
      toast.error('AI library not ready yet, please wait a moment and try again.')
      return
    }

    setIsLoadingModel(true)
    setLoadingMessage('Connecting to model...')
    setLoadingProgress(0)

    try {
      const model = await transformersPipeline(
        'image-to-text',
        'Xenova/vit-gpt2-image-captioning',
        {
          progress_callback: (progress: any) => {
            if (progress.status === 'progress' && progress.progress !== undefined) {
              setLoadingProgress(Math.round(progress.progress))
              setLoadingMessage(`Downloading model... ${Math.round(progress.progress)}%`)
            } else if (progress.status === 'done') {
              setLoadingMessage('Initializing model...')
            }
          },
        }
      )
      setCaptioner(model)
      setIsLoadingModel(false)
      setLoadingMessage('')
      toast.success('Model loaded! 🎉 Drop an image to generate a caption.')
    } catch (error) {
      console.error('Failed to load model:', error)
      setIsLoadingModel(false)
      setLoadingMessage('')
      toast.error('Failed to load model. Please refresh and try again.')
    }
  }

  // Handle image drop / selection
  const onDrop = useCallback((acceptedFiles: File[], fileRejections: any[]) => {
    setErrorMsg(null)

    if (fileRejections.length > 0) {
      setErrorMsg('Invalid file. Please upload a JPEG, PNG, or WEBP image under 10MB.')
      return
    }

    const file = acceptedFiles[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string)
      setCaption(null)
      setInferenceTime(null)
    }
    reader.readAsDataURL(file)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    disabled: isGenerating || isLoadingModel,
  })

  // Generate caption — pass the data URL string directly (fixes "Unsupported input type: object")
  const generateCaption = async () => {
    if (!imagePreview) {
      toast.error('Please upload an image first')
      return
    }
    if (!captioner) {
      toast.error('Please load the AI model first')
      return
    }

    setIsGenerating(true)
    setCaption(null)
    setInferenceTime(null)
    const startTime = performance.now()

    try {
      // Pass the data URL string directly — Transformers.js v2 handles this correctly
      const result = await captioner(imagePreview, {
        max_new_tokens: 50,
        num_beams: 5,
        do_sample: false,
      })

      const time = Math.round(performance.now() - startTime)
      const text =
        Array.isArray(result)
          ? result[0]?.generated_text || result[0]?.text || ''
          : result?.generated_text || result?.text || ''

      if (!text) throw new Error('Empty caption returned')

      setCaption(text.trim())
      setInferenceTime(time)
      toast.success(`Caption ready in ${time}ms! ✨`)
    } catch (error: any) {
      console.error('Caption generation failed:', error)
      toast.error('Failed to generate caption. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const scrollToDemo = () => {
    demoRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="relative min-h-screen overflow-hidden text-gray-900 dark:text-gray-100">
      <Toaster position="top-center" />

      {/* Background blobs */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary-900/20 blur-[120px] animate-pulse-subtle"></div>
        <div
          className="absolute top-[20%] right-[-10%] w-[40%] h-[60%] rounded-full bg-cyan-900/10 blur-[150px] animate-pulse-subtle"
          style={{ animationDelay: '2s' }}
        ></div>
        <div className="hidden md:block absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4IiBoZWlnaHQ9IjgiPgo8cmVjdCB3aWR0aD0iOCIgaGVpZ2h0PSI4IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDIiLz4KPC9zdmc+')] opacity-50 z-0"></div>
      </div>

      <Navbar />

      {/* ── Hero Section ── */}
      <section className="relative container mx-auto px-4 pt-32 pb-20 z-10">
        <div className="text-center mb-12 animate-slide-up max-w-4xl mx-auto">
          {/* Live badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-button text-xs font-semibold text-primary-400 mb-6 border border-primary-500/30">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
            </span>
            VisionCaption AI 2.0 — Browser-powered, no API needed
          </div>

          <h1 className="text-5xl md:text-7xl font-extrabold tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-white via-indigo-200 to-cyan-200 mb-6 drop-shadow-lg leading-tight">
            Generate Intelligent <br className="hidden md:block" /> Image Captions with AI
          </h1>
          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed mb-10">
            100% browser-based inference. No backend, no API keys, no rate limits. Your images never
            leave your device.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={scrollToDemo}
              className="relative group px-8 py-4 rounded-xl font-bold text-white bg-primary-600 hover:bg-primary-500 transition-all duration-300 w-full sm:w-auto shadow-[0_0_20px_rgba(99,102,241,0.4)] hover:shadow-[0_0_30px_rgba(99,102,241,0.6)]"
            >
              <div className="absolute inset-0 w-full h-full rounded-xl -z-10 group-hover:animate-pulse-glow glow-border"></div>
              Try It Now — Free
            </button>
            <div className="flex items-center gap-2 px-6 py-4 rounded-xl glass-button text-sm text-gray-300 font-medium">
              <span className="text-green-400">✓</span> Private &nbsp;
              <span className="text-green-400">✓</span> Offline-capable &nbsp;
              <span className="text-green-400">✓</span> No signup
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 animate-bounce-soft hidden sm:flex flex-col items-center">
          <span className="text-xs text-gray-500 mb-2 uppercase tracking-widest font-semibold">
            Scroll
          </span>
          <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </section>

      {/* ── Demo Section ── */}
      <section ref={demoRef} className="relative z-20 pb-24 px-4 sm:px-6">
        <div className="max-w-4xl mx-auto animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <div className="glass-panel rounded-3xl p-2 sm:p-6 md:p-10 relative">
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>

            <div className="space-y-8 relative z-10 bg-[#0B0F19]/60 dark:bg-[#111827]/60 rounded-2xl p-4 sm:p-8 border border-white/5">

              {/* Step indicator */}
              <div className="flex items-center gap-3 flex-wrap">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${captioner ? 'bg-green-900/40 text-green-300 border-green-500/40' : 'bg-gray-800 text-gray-400 border-gray-600/40'}`}>
                  {captioner ? '✓ Model Ready' : '① Load Model'}
                </span>
                <span className="text-gray-600">→</span>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${imagePreview ? 'bg-blue-900/40 text-blue-300 border-blue-500/40' : 'bg-gray-800 text-gray-400 border-gray-600/40'}`}>
                  ② Upload Image
                </span>
                <span className="text-gray-600">→</span>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${caption ? 'bg-primary-900/40 text-primary-300 border-primary-500/40' : 'bg-gray-800 text-gray-400 border-gray-600/40'}`}>
                  ③ Get Caption
                </span>
              </div>

              {/* ── Step 1: Load Model ── */}
              {!captioner && !isLoadingModel && (
                <div className="glass rounded-2xl p-6 sm:p-8 border border-white/10">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-primary-600/20 flex items-center justify-center flex-shrink-0 border border-primary-500/30">
                      <svg className="w-6 h-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-gray-100 mb-1">Load the AI Model</h3>
                      <p className="text-sm text-gray-400 mb-4">
                        Downloads once (~350MB) and caches in your browser — instant on return visits. The model runs entirely on your device.
                      </p>
                      <button
                        onClick={loadModel}
                        className="px-6 py-3 rounded-xl font-bold text-white bg-primary-600 hover:bg-primary-500 transition-all duration-300 shadow-[0_0_20px_rgba(99,102,241,0.3)] hover:shadow-[0_0_30px_rgba(99,102,241,0.5)] text-sm"
                      >
                        🚀 Load AI Model
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* ── Model Loading Progress ── */}
              {isLoadingModel && (
                <div className="glass rounded-2xl p-6 sm:p-8 border border-white/10">
                  <div className="flex items-center gap-3 mb-4">
                    <svg className="animate-spin w-5 h-5 text-primary-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <circle cx="12" cy="12" r="10" strokeWidth="2" strokeOpacity="0.2"></circle>
                      <path d="M12 2a10 10 0 0 1 10 10" strokeWidth="2" strokeLinecap="round"></path>
                    </svg>
                    <span className="text-gray-300 font-medium">{loadingMessage || 'Loading model...'}</span>
                  </div>
                  <div className="w-full bg-gray-700/60 rounded-full h-3 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-primary-500 to-cyan-500 h-3 rounded-full transition-all duration-300"
                      style={{ width: `${Math.max(loadingProgress, 5)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-3">
                    This only happens once. The model will be cached for instant future use.
                  </p>
                </div>
              )}

              {/* ── Step 2 & 3: Upload + Caption ── */}
              {captioner && (
                <>
                  {/* Dropzone */}
                  <div className="w-full relative">
                    <div
                      {...getRootProps()}
                      role="button"
                      tabIndex={0}
                      aria-label="Upload an image for captioning"
                      className={`
                        relative outline-none rounded-2xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-300
                        backdrop-blur-2xl border-2 border-dashed
                        ${isDragActive
                          ? 'border-primary-400 bg-primary-900/20 shadow-[0_0_30px_rgba(99,102,241,0.3)]'
                          : 'border-white/20 bg-white/5 hover:border-primary-500/50 hover:bg-white/10 hover:shadow-[0_0_15px_rgba(99,102,241,0.1)]'
                        }
                        ${isGenerating ? 'opacity-60 cursor-not-allowed' : ''}
                        ${errorMsg ? 'border-red-500/50 bg-red-900/10' : ''}
                        focus-visible:ring-4 focus-visible:ring-primary-500/50
                      `}
                    >
                      <input {...getInputProps()} />

                      {imagePreview ? (
                        <div className="space-y-6 relative z-10">
                          <div className="relative inline-block">
                            <img
                              src={imagePreview}
                              alt="Preview to caption"
                              className="max-h-72 mx-auto rounded-xl shadow-[0_8px_30px_rgba(0,0,0,0.4)] border border-white/10"
                            />
                          </div>
                          {!isGenerating && (
                            <p className="text-sm text-gray-400">
                              Click or drag another image to replace
                            </p>
                          )}
                        </div>
                      ) : (
                        <div className="space-y-4 relative z-10 py-6">
                          <div className={`w-20 h-20 mx-auto rounded-2xl flex items-center justify-center transition-all duration-300 ${isDragActive ? 'bg-primary-500/20 scale-110' : 'bg-white/5'}`}>
                            <svg className={`w-10 h-10 ${isDragActive ? 'text-primary-400' : 'text-gray-400'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                          </div>
                          <div>
                            <p className={`text-lg sm:text-xl font-semibold mb-2 transition-colors ${isDragActive ? 'text-primary-300' : 'text-gray-200'}`}>
                              {isDragActive ? 'Drop image to analyze' : 'Drag & drop image or click to browse'}
                            </p>
                            <p className="text-sm text-gray-500">PNG, JPG, WEBP up to 10MB</p>
                          </div>
                        </div>
                      )}
                    </div>

                    {errorMsg && (
                      <div className="mt-4 px-4 py-3 bg-red-900/20 border border-red-500/30 rounded-xl flex items-center gap-3 text-red-200 text-sm">
                        <svg className="w-5 h-5 text-red-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        {errorMsg}
                      </div>
                    )}
                  </div>

                  {/* Generate button */}
                  {imagePreview && (
                    <button
                      onClick={generateCaption}
                      disabled={isGenerating}
                      className="w-full py-4 rounded-xl font-bold text-white bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-[0_0_20px_rgba(99,102,241,0.3)] hover:shadow-[0_0_30px_rgba(99,102,241,0.5)] flex items-center justify-center gap-3"
                    >
                      {isGenerating ? (
                        <>
                          <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <circle cx="12" cy="12" r="10" strokeWidth="2" strokeOpacity="0.2"></circle>
                            <path d="M12 2a10 10 0 0 1 10 10" strokeWidth="2" strokeLinecap="round"></path>
                          </svg>
                          Generating Caption...
                        </>
                      ) : (
                        <>✨ Generate Caption</>
                      )}
                    </button>
                  )}

                  {/* Caption result */}
                  {isGenerating && !caption && (
                    <div className="glass rounded-2xl p-8 relative overflow-hidden flex flex-col items-center justify-center space-y-4">
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary-500/10 to-transparent animate-[shimmer_2s_infinite]"></div>
                      <span className="text-gray-300 font-medium tracking-wide">AI is analyzing your image...</span>
                    </div>
                  )}

                  {caption && !isGenerating && (
                    <CaptionResult caption={caption} inferenceTime={inferenceTime} />
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ── Features Section ── */}
      <section className="relative z-10 py-24 bg-gray-900/40 border-y border-white/5">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">
              Why Browser-Based AI?
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              No backend infrastructure. Your images never leave your device.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6 lg:gap-8 max-w-6xl mx-auto">
            <FeatureCard
              icon={
                <svg className="w-8 h-8 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              }
              title="100% Private"
              description="Images are processed entirely in your browser using WebAssembly. Zero data sent to any server."
              colorClass="from-primary-500/20 to-indigo-500/20"
            />
            <FeatureCard
              icon={
                <svg className="w-8 h-8 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              }
              title="No Limits"
              description="No API keys, no rate limits, no sign-up required. Generate as many captions as you like for free."
              colorClass="from-cyan-500/20 to-blue-500/20"
            />
            <FeatureCard
              icon={
                <svg className="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              }
              title="ViT-GPT2 Model"
              description="Powered by Xenova/vit-gpt2-image-captioning via ONNX Runtime — optimized for browser execution."
              colorClass="from-emerald-500/20 to-green-500/20"
            />
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="relative z-10 py-24 pb-32">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">
              How It Works
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">Three simple steps to AI-powered captions.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              { step: '01', title: 'Load Model', desc: 'Click "Load AI Model" to download the ViT-GPT2 model (~350MB) once. It\'s cached in your browser forever.' },
              { step: '02', title: 'Upload Image', desc: 'Drag & drop or select any image (PNG, JPG, WEBP). Your image stays local — nothing is uploaded.' },
              { step: '03', title: 'Get Caption', desc: 'Hit "Generate Caption" and get an AI-generated description in 1–5 seconds, entirely on your device.' },
            ].map(({ step, title, desc }) => (
              <div key={step} className="glass rounded-2xl p-8 border border-white/5 text-center">
                <div className="text-5xl font-extrabold text-primary-500/30 mb-4">{step}</div>
                <h3 className="text-xl font-bold text-gray-100 mb-3">{title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="relative z-10 glass border-t border-white/10 dark:border-white/5 py-8 opacity-80 backdrop-blur-md">
        <div className="container mx-auto px-4 flex flex-col md:flex-row justify-between items-center text-sm text-gray-500">
          <div>© 2026 VisionCaption AI. All rights reserved.</div>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <span className="hover:text-white cursor-pointer transition">Privacy</span>
            <span className="hover:text-white cursor-pointer transition">Terms</span>
            <span className="hover:text-white cursor-pointer transition">GitHub</span>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({
  icon,
  title,
  description,
  colorClass,
}: {
  icon: React.ReactNode
  title: string
  description: string
  colorClass: string
}) {
  return (
    <div className="group glass rounded-2xl p-8 hover:-translate-y-2 hover:shadow-[0_10px_40px_-10px_rgba(99,102,241,0.3)] transition-all duration-300 relative overflow-hidden border border-white/5 hover:border-white/10">
      <div
        className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl ${colorClass} blur-[50px] opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
      ></div>
      <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mb-6 shadow-inner group-hover:scale-110 transition-transform duration-300 ease-out border border-white/10">
        {icon}
      </div>
      <h3 className="text-2xl font-bold text-gray-100 mb-3 tracking-wide">{title}</h3>
      <p className="text-gray-400 leading-relaxed text-sm">{description}</p>
    </div>
  )
}
