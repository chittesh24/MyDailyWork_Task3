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
  const { apiKey } = useAuthStore()

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File too large. Maximum size is 5MB.')
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

      // Use demo endpoint (no auth required) for easier deployment
      // For production with auth, use: `${API_URL}/caption`
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
      toast.error(message)
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
    disabled: isUploading,
  })

  return (
    <div className="glass rounded-2xl shadow-xl p-8">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all
          ${isDragActive 
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
          }
          ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        {preview ? (
          <div className="space-y-4">
            <img 
              src={preview} 
              alt="Preview" 
              className="max-h-64 mx-auto rounded-lg shadow-lg"
            />
            {!isUploading && (
              <p className="text-gray-600 dark:text-gray-400">
                Drop another image to replace
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-6xl">📸</div>
            <div>
              <p className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {isDragActive ? 'Drop image here' : 'Drop image or click to upload'}
              </p>
              <p className="text-gray-500 dark:text-gray-400">
                Supports JPEG and PNG (max 5MB)
              </p>
            </div>
          </div>
        )}
      </div>

      {isUploading && (
        <div className="mt-4">
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
            <div className="bg-primary-600 h-full animate-pulse" style={{ width: '100%' }}></div>
          </div>
        </div>
      )}
    </div>
  )
}
