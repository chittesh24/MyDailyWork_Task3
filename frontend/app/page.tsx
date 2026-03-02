'use client'
export const dynamic = 'force-dynamic'
import React, { useState, useCallback, useEffect, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import toast, { Toaster } from 'react-hot-toast'
import Navbar from '@/components/Navbar'
import CaptionResult from '@/components/CaptionResult'

let transformersPipeline: any = null

export default function Home() {
  const [captioner, setCaptioner] = useState<any>(null)
  const [isLoadingModel, setIsLoadingModel] = useState(false)
  const [loadingProgress, setLoadingProgress] = useState(0)
  const [loadingMessage, setLoadingMessage] = useState('')
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const imageFileRef = useRef<File | null>(null)
  const [caption, setCaption] = useState<string | null>(null)
  const [inferenceTime, setInferenceTime] = useState<number | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const demoRef = useRef<HTMLDivElement>(null)

  // Load Transformers.js
  useEffect(() => {
    const loadTransformers = async () => {
      try {
        const mod = await import('@xenova/transformers')

        const pipelineFn = mod.pipeline
        transformersPipeline = pipelineFn

        // ✅ Stable browser config
        mod.env.allowLocalModels = false
        mod.env.allowRemoteModels = true
        mod.env.useBrowserCache = true

        // ✅ Disable workers (prevents crashes)
        mod.env.backends.onnx.wasm.numThreads = 1
        mod.env.backends.onnx.wasm.simd = false
        mod.env.backends.onnx.wasm.proxy = false

        console.log('Transformers initialized correctly')
      } catch (error) {
        console.error('Failed to load Transformers.js:', error)
      }
    }

    loadTransformers()
  }, [])

  const loadModel = async () => {
    if (!transformersPipeline) {
      toast.error('AI library not ready yet.')
      return
    }

    setIsLoadingModel(true)
    setLoadingProgress(0)
    setLoadingMessage('Connecting to model...')

    try {
      const model = await transformersPipeline(
        'image-to-text',
        'Xenova/blip-image-captioning-base',
        {
          progress_callback: (progress: any) => {
            if (progress.status === 'progress' && progress.progress !== undefined) {
              setLoadingProgress(Math.round(progress.progress))
              setLoadingMessage(`Downloading model... ${Math.round(progress.progress)}%`)
            } else if (progress.status === 'done') {
              setLoadingMessage('Finalizing model...')
            }
          },
        }
      )

      setCaptioner(model)
      toast.success('Model loaded successfully!')
    } catch (error) {
      console.error(error)
      toast.error('Model loading failed.')
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

    imageFileRef.current = file

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

  const generateCaption = async () => {
    if (!imageFileRef.current) {
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
      // ✅ Create HTMLImageElement (MOST STABLE INPUT)
      const img = new Image()
      img.src = URL.createObjectURL(imageFileRef.current)

      await new Promise((resolve) => {
        img.onload = resolve
      })

      const result = await captioner(img, {
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
    } catch (error) {
      console.error('Caption generation failed:', error)
      toast.error('Failed to generate caption.')
    } finally {
      setIsGenerating(false)
    }
  }

  const scrollToDemo = () => {
    demoRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="min-h-screen">
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
        {!captioner && !isLoadingModel && (
          <button
            onClick={loadModel}
            className="w-full py-3 bg-indigo-600 text-white rounded-lg"
          >
            Load AI Model (~350MB)
          </button>
        )}

        {isLoadingModel && (
          <div>
            <p>{loadingMessage}</p>
            <div className="w-full bg-gray-300 h-2 rounded">
              <div
                className="bg-indigo-600 h-2 rounded"
                style={{ width: `${loadingProgress}%` }}
              />
            </div>
          </div>
        )}

        {captioner && (
          <>
            <div
              {...getRootProps()}
              className={`p-10 border-2 border-dashed rounded-lg text-center cursor-pointer ${
                isDragActive ? 'border-indigo-500' : 'border-gray-400'
              }`}
            >
              <input {...getInputProps()} />
              {imagePreview ? (
                <img
                  src={imagePreview}
                  className="max-h-64 mx-auto"
                  alt="Preview"
                />
              ) : (
                <p>Drag & drop image or click to upload</p>
              )}
            </div>

            {imagePreview && (
              <button
                onClick={generateCaption}
                disabled={isGenerating}
                className="w-full py-3 bg-indigo-600 text-white rounded-lg"
              >
                {isGenerating ? 'Generating...' : 'Generate Caption'}
              </button>
            )}

            {caption && (
              <CaptionResult
                caption={caption}
                inferenceTime={inferenceTime}
              />
            )}
          </>
        )}
      </section>
    </div>
  )
}