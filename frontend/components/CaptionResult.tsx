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
    toast.success('Caption copied to clipboard!', { icon: '📋' })
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, ease: [0.23, 1, 0.32, 1] }}
      className="relative w-full"
    >
      {/* Glow underlay */}
      <div className="absolute inset-0 bg-primary-500/10 blur-xl rounded-2xl"></div>

      <div className="relative glass-panel rounded-2xl p-6 sm:p-8 animate-fade-in border-t border-l border-white/20">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary-500/20 to-cyan-500/20 flex items-center justify-center border border-white/10 shadow-[0_0_15px_rgba(99,102,241,0.2)]">
              <span className="text-xl">✨</span>
            </div>
            <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-white drop-shadow-sm">
              Generated Caption
            </h3>
          </div>

          <button
            onClick={copyToClipboard}
            className={`
               group relative flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 overflow-hidden
               ${copied
                ? 'text-white bg-green-500/20 border border-green-500/50 shadow-[0_0_15px_rgba(16,185,129,0.3)]'
                : 'text-gray-300 glass-button border-white/10 hover:text-white hover:border-primary-400 hover:shadow-[0_0_15px_rgba(99,102,241,0.3)]'
              }
            `}
          >
            {copied && <span className="absolute inset-0 bg-green-500/20 animate-pulse-subtle"></span>}
            <span className="relative z-10">{copied ? '✓ Copied' : '📋 Copy Text'}</span>
          </button>
        </div>

        <div className="relative bg-[#0B0F19]/80 backdrop-blur-md rounded-xl p-6 border border-white/5 shadow-inner">
          <p className="text-lg sm:text-xl text-gray-200 leading-relaxed font-medium">
            {caption}
          </p>
        </div>

        {inferenceTime && (
          <div className="mt-6 flex items-center gap-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
            </span>
            <span>Generated in {inferenceTime.toFixed(0)}ms</span>
          </div>
        )}
      </div>
    </motion.div>
  )
}
