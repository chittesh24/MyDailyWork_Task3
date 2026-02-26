'use client'

import { useEffect, useState } from 'react'

export default function ThemeCustomizer() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    
    // Load saved preferences
    const savedTheme = localStorage.getItem('app-theme') || 'blue'
    const savedFontSize = localStorage.getItem('app-fontSize') || 'medium'
    const savedAnimations = localStorage.getItem('app-animations') !== 'false'
    
    document.documentElement.setAttribute('data-theme', savedTheme)
    document.documentElement.setAttribute('data-font-size', savedFontSize)
    document.documentElement.setAttribute('data-animations', savedAnimations.toString())
  }, [])

  if (!mounted) return null

  return null
}
