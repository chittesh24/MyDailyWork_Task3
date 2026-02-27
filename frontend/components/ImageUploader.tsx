'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/store/authStore'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ImageUploaderProps {
  onCaptionGenerated: (data: { caption: string; inference_time_ms: number }) => void
  onUploadStart: () => void
}

export default function ImageUploader({ onCaptionGenerated, onUploadStart }: ImageUploaderProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const { apiKey } = useAuthStore()

  const onDrop = useCallback(async (acceptedFiles: File[], fileRejections: any[]) => {
    setErrorMsg(null)

    if (fileRejections.length > 0) {
      setErrorMsg('Invalid file. Please upload a JPEG or PNG under 5MB.')
      return
    }

    const file = acceptedFiles[0]
    if (!file) return

    // Validate file size (5MB) - Extra safety
    if (file.size > 5 * 1024 * 1024) {
      setErrorMsg('File too large. Maximum size is 5MB.')
      return
    }

    // Create preview
    const reader = new FileReader()
    reader.onload = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)

    // Upload and generate caption
    setIsUploading(true)
    onUploadStart()

    try {
      const formData = new FormData()
      formData.append('file', file)

      // Use demo endpoint
      const response = await axios.post(`${API_URL}/demo/caption`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      onCaptionGenerated(response.data)
      toast.success('Caption generated successfully!')
    } catch (error: any) {
      console.error('Error generating caption:', error)
      const message = error.response?.data?.detail || 'Failed to generate caption'
      setErrorMsg(message)
    } finally {
      setIsUploading(false)
    }
  }, [apiKey, onCaptionGenerated, onUploadStart])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024,
    disabled: isUploading,
  })

  return (
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
            ? 'border-primary-400 bg-primary-900/20 shadow-[0_0_20px_rgba(99,102,241,0.2),inset_0_0_30px_rgba(99,102,241,0.15)] sm:shadow-[0_0_30px_rgba(99,102,241,0.3),inset_0_0_50px_rgba(99,102,241,0.2)]'
            : 'border-white/20 bg-white/5 shadow-md sm:shadow-lg hover:border-primary-500/50 hover:bg-white/10 hover:shadow-[0_0_15px_rgba(99,102,241,0.1)]'
          }
          ${isUploading ? 'opacity-50 cursor-not-allowed border-gray-600' : ''}
          ${errorMsg ? 'animate-vibrate border-red-500/50 bg-red-900/10' : ''}
          focus-visible:ring-4 focus-visible:ring-primary-500/50 focus-visible:border-primary-400
        `}
      >
        <input {...getInputProps()} />

        {preview ? (
          <div className="space-y-6 relative z-10">
            <div className="relative inline-block">
              <img
                src={preview}
                alt="Preview to caption"
                className="max-h-64 mx-auto rounded-xl shadow-[0_8px_30px_rgba(0,0,0,0.4)] border border-white/10"
              />
              <div className="absolute inset-0 rounded-xl shadow-[inset_0_0_0_1px_rgba(255,255,255,0.1)] pointer-events-none"></div>
            </div>
            {!isUploading && !errorMsg && (
              <p className="text-sm font-medium text-gray-400 group-hover:text-gray-300 transition-colors">
                Click or drag another image to replace
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-4 relative z-10 py-6">
            <div className={`w-20 h-20 mx-auto rounded-2xl flex items-center justify-center transition-all duration-300 ${isDragActive ? 'bg-primary-500/20 scale-110 shadow-[0_0_20px_rgba(99,102,241,0.3)]' : 'bg-white/5'}`}>
              <svg className={`w-10 h-10 ${isDragActive ? 'text-primary-400' : 'text-gray-400'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <p className={`text-lg sm:text-xl font-semibold mb-2 transition-colors ${isDragActive ? 'text-primary-300 text-glow' : 'text-gray-200'}`}>
                {isDragActive ? 'Drop image to analyze' : 'Drag & drop image or click to browse'}
              </p>
              <p className="text-sm text-gray-500">
                Supports High-Res JPEG and PNG (max 5MB)
              </p>
            </div>
          </div>
        )}
      </div>

      {errorMsg && (
        <div className="mt-4 px-4 py-3 bg-red-900/20 border border-red-500/30 rounded-xl flex items-center gap-3 text-red-200 text-sm animate-fade-in">
          <svg className="w-5 h-5 text-red-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          {errorMsg}
        </div>
      )}
    </div>
  )
}
