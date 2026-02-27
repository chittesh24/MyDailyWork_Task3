/**
 * Demo page for Transformers.js Browser-based Captioning
 * Standalone page showcasing the new browser inference
 */

'use client';

import { Toaster } from 'react-hot-toast';
import Navbar from '@/components/Navbar';
import ImageCaptionGenerator from '@/components/ImageCaptionGenerator';

export default function DemoPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Navbar />
      <Toaster position="top-center" />
      
      <main className="container mx-auto px-4 py-8">
        <ImageCaptionGenerator />

        {/* Features Section */}
        <div className="mt-16 grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <FeatureCard 
            icon="🖥️"
            title="Browser-Based AI"
            description="Runs 100% in your browser - no server needed!"
          />
          <FeatureCard 
            icon="💰"
            title="Completely Free"
            description="No API limits, no costs - unlimited captions forever"
          />
          <FeatureCard 
            icon="🔒"
            title="Privacy First"
            description="Your images never leave your device"
          />
        </div>

        {/* Technical Details */}
        <div className="mt-16 max-w-5xl mx-auto bg-white dark:bg-gray-800 rounded-lg p-8 shadow-lg">
          <h2 className="text-2xl font-bold mb-6">How It Works</h2>
          <div className="space-y-4 text-gray-600 dark:text-gray-300">
            <div className="flex items-start gap-4">
              <span className="text-2xl">🧠</span>
              <div>
                <h3 className="font-semibold text-gray-800 dark:text-gray-200">Transformers.js</h3>
                <p>Uses @xenova/transformers library to run state-of-the-art vision models directly in your browser using WebAssembly and WebGL acceleration.</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <span className="text-2xl">⚡</span>
              <div>
                <h3 className="font-semibold text-gray-800 dark:text-gray-200">Optimized Models</h3>
                <p>Choose from BLIP-base (~500MB), BLIP-large (~900MB), or GIT-base (~700MB) models optimized for browser inference with ONNX runtime.</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <span className="text-2xl">💾</span>
              <div>
                <h3 className="font-semibold text-gray-800 dark:text-gray-200">Smart Caching</h3>
                <p>Models are downloaded once and cached in your browser. Future sessions load instantly without re-downloading.</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <span className="text-2xl">🔄</span>
              <div>
                <h3 className="font-semibold text-gray-800 dark:text-gray-200">Hybrid Fallback</h3>
                <p>Automatically falls back to server API if browser inference fails, ensuring reliability.</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">{title}</h3>
      <p className="text-gray-600 dark:text-gray-300">{description}</p>
    </div>
  );
}
