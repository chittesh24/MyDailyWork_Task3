'use client'

import { useCallback, useState, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import { pipeline } from '@xenova/transformers'

interface ImageUploaderProps {
  onCaptionGenerated: (data: { caption: string; inference_time_ms: number }) => void
  onUploadStart: () => void
}

export default function ImageUploader({ onCaptionGenerated, onUploadStart }: ImageUploaderProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const captionerRef = useRef<any>(null)

  // Load model once
  const loadModel = async () => {
    if (!captionerRef.current) {
      toast.loading('Loading AI model (~350MB first time)...')
      captionerRef.current = await pipeline(
        'image-to-text',
        'Xenova/vit-gpt2-image-captioning'
      )
      toast.dismiss()
      toast.success('Model Ready')
    }
  }

  const fileToImage = (file: File): Promise<HTMLImageElement> => {
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = reject
      img.src = URL.createObjectURL(file)
    })
  }

  const onDrop = useCallback(async (acceptedFiles: File[], fileRejections: any[]) => {
    setErrorMsg(null)

    if (fileRejections.length > 0) {
      setErrorMsg('Invalid file. Please upload JPEG/PNG under 5MB.')
      return
    }

    const file = acceptedFiles[0]
    if (!file) return

    if (file.size > 5 * 1024 * 1024) {
      setErrorMsg('File too large. Maximum size is 5MB.')
      return
    }

    setPreview(URL.createObjectURL(file))
    setIsUploading(true)
    onUploadStart()

    try {
      await loadModel()

      const imageElement = await fileToImage(file)

      const start = performance.now()
      const result = await captionerRef.current(imageElement)
      const end = performance.now()

      const caption = result[0].generated_text

      onCaptionGenerated({
        caption,
        inference_time_ms: Math.round(end - start)
      })

      toast.success('Caption generated successfully!')
    } catch (err) {
      console.error('Caption generation failed:', err)
      setErrorMsg('Failed to generate caption. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }, [onCaptionGenerated, onUploadStart])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/webp': ['.webp']
    },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024,
    disabled: isUploading,
  })

  return (
    <div className="w-full relative">
      <div
        {...getRootProps()}
        className="rounded-2xl p-8 text-center border-2 border-dashed border-white/20 bg-white/5 backdrop-blur-xl cursor-pointer"
      >
        <input {...getInputProps()} />

        {preview ? (
          <img src={preview} alt="Preview" className="max-h-64 mx-auto rounded-xl" />
        ) : (
          <p className="text-gray-300">
            {isDragActive ? 'Drop image here' : 'Drag & drop image or click to browse'}
          </p>
        )}
      </div>

      {errorMsg && (
        <div className="mt-4 text-red-400 text-sm">
          {errorMsg}
        </div>
      )}
    </div>
  )
}