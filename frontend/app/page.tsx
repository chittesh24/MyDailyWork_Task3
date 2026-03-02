'use client'
import React, { useState, useCallback, useEffect, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import toast, { Toaster } from 'react-hot-toast'
import Navbar from '@/components/Navbar'
import CaptionResult from '@/components/CaptionResult'

// Store pipeline outside React state — React clones/serializes state
// which breaks the Pipeline object. useRef holds the live reference.
const captionerRef = { current: null as any }

export default function Home() {
  const [modelLoaded, setModelLoaded] = useState(false)
  const [isLoadingModel, setIsLoadingModel] = useState(false)
  const [loadingProgress, setLoadingProgress] = useState(0)
  const [loadingMessage, setLoadingMessage] = useState('')
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [caption, setCaption] = useState<string | null>(null)
  const [inferenceTime, setInferenceTime] = useState<number | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isMounted, setIsMounted] = useState(false)
  const imageDataUrlRef = useRef<string | null>(null)
  const demoRef = useRef<HTMLDivElement>(null)

  // Prevent SSR/hydration mismatch — only render interactive UI client-side
  useEffect(() => { setIsMounted(true) }, [])

  const loadModel = async () => {
    setIsLoadingModel(true)
    setLoadingProgress(0)
    setLoadingMessage('Loading AI library...')

    try {
      // Dynamically import to ensure browser-only execution
      const { pipeline, env } = await import('@xenova/transformers')

      // Configure for browser WASM execution
      env.allowLocalModels = false
      env.allowRemoteModels = true
      env.useBrowserCache = true
      env.backends.onnx.wasm.numThreads = 1

      setLoadingMessage('Downloading model files...')

      const pipe = await pipeline(
        'image-to-text',
        'Xenova/vit-gpt2-image-captioning',
        {
          progress_callback: (p: any) => {
            if (p.status === 'progress' && p.progress != null) {
              const pct = Math.round(p.progress)
              setLoadingProgress(pct)
              setLoadingMessage(`Downloading model... ${pct}%`)
            } else if (p.status === 'done') {
              setLoadingMessage('Finalizing...')
            }
          },
        }
      )

      // Store in module-level ref — NOT in React state
      captionerRef.current = pipe
      setModelLoaded(true)
      toast.success('Model loaded! Upload an image to caption it.')
    } catch (err: any) {
      console.error('Model load error:', err)
      toast.error(`Failed to load model: ${err?.message || err}`)
    } finally {
      setIsLoadingModel(false)
      setLoadingMessage('')
    }
  }

  const onDrop = useCallback((acceptedFiles: File[], fileRejections: any[]) => {
    if (fileRejections.length > 0) {
      toast.error('Invalid file. Use PNG, JPG, WEBP under 10MB.')
      return
    }
    const file = acceptedFiles[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      const dataUrl = e.target?.result as string
      imageDataUrlRef.current = dataUrl
      setImagePreview(dataUrl)
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

  const generateCaption = async () => {
    if (!imageDataUrlRef.current) {
      toast.error('Please upload an image first')
      return
    }
    if (!captionerRef.current) {
      toast.error('Please load the AI model first')
      return
    }

    setIsGenerating(true)
    setCaption(null)
    setInferenceTime(null)
    const startTime = performance.now()

    try {
      // Pass data URL string — the only input type supported by @xenova/transformers v2
      const result = await captionerRef.current(imageDataUrlRef.current, {
        max_new_tokens: 50,
        num_beams: 4,
        do_sample: false,
      })

      const time = Math.round(performance.now() - startTime)
      const text = Array.isArray(result)
        ? result[0]?.generated_text || ''
        : result?.generated_text || ''

      if (!text) throw new Error('Empty caption returned')

      setCaption(text.trim())
      setInferenceTime(time)
      toast.success(`Caption ready in ${time}ms! ✨`)
    } catch (err: any) {
      console.error('Caption generation failed:', err)
      toast.error(`Failed: ${err?.message || 'Unknown error'}`)
    } finally {
      setIsGenerating(false)
    }
  }

  const scrollToDemo = () => {
    demoRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="min-h-screen" suppressHydrationWarning>
      <Toaster position="top-center" />
      <Navbar />

      <section className="text-center pt-24 pb-12">
        <h1 className="text-4xl font-bold mb-4">
          Browser-Based AI Image Captioning
        </h1>
        <p className="text-gray-500 mb-6">
          100% client-side. No backend. No API keys.
        </p>
        <button
          onClick={scrollToDemo}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg"
        >
          Try Now
        </button>
      </section>

      <section ref={demoRef} className="max-w-3xl mx-auto p-6 space-y-6">
        {/* Only render interactive UI after client-side mount to avoid hydration mismatch */}
        {isMounted && (
          <>
            {!modelLoaded && !isLoadingModel && (
              <button
                onClick={loadModel}
                className="w-full py-3 bg-indigo-600 text-white rounded-lg font-semibold"
              >
                Load AI Model (~250MB)
              </button>
            )}

            {isLoadingModel && (
              <div className="space-y-2">
                <p className="text-sm text-gray-500">{loadingMessage}</p>
                <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${loadingProgress}%` }}
                  />
                </div>
                <p className="text-xs text-gray-400 text-right">{loadingProgress}%</p>
              </div>
            )}

            {modelLoaded && (
              <>
                <div
                  {...getRootProps()}
                  className={`p-10 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${
                    isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-400'
                  }`}
                >
                  <input {...getInputProps()} />
                  {imagePreview ? (
                    <img src={imagePreview} className="max-h-64 mx-auto rounded" alt="Preview" />
                  ) : (
                    <p className="text-gray-500">Drag & drop an image or click to upload</p>
                  )}
                </div>

                {imagePreview && (
                  <button
                    onClick={generateCaption}
                    disabled={isGenerating}
                    className="w-full py-3 bg-indigo-600 text-white rounded-lg font-semibold disabled:opacity-50"
                  >
                    {isGenerating ? 'Generating caption...' : 'Generate Caption'}
                  </button>
                )}

                {caption && (
                  <CaptionResult caption={caption} inferenceTime={inferenceTime} />
                )}
              </>
            )}
          </>
        )}
      </section>
    </div>
  )
}