'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import toast from 'react-hot-toast'

interface CaptionResultProps {
  caption: string
  inferenceTime: number | null
}

export default function CaptionResult({ caption, inferenceTime }: CaptionResultProps) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = () => {
    navigator.clipboard.writeText(caption)
    setCopied(true)
    toast.success('Caption copied to clipboard!')
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass rounded-2xl shadow-xl p-8"
    >
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
          Generated Caption
        </h3>
        <button
          onClick={copyToClipboard}
          className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition flex items-center gap-2"
        >
          {copied ? '✓ Copied' : '📋 Copy'}
        </button>
      </div>

      <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6 mb-4">
        <p className="text-lg text-gray-800 dark:text-gray-200 leading-relaxed">
          {caption}
        </p>
      </div>

      {inferenceTime && (
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <span>⚡</span>
          <span>Generated in {inferenceTime.toFixed(0)}ms</span>
        </div>
      )}
    </motion.div>
  )
}
