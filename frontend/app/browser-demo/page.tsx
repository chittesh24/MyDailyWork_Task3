/**
 * Pure Browser-Based Image Captioning Demo
 * No API needed - 100% client-side using Transformers.js
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import toast, { Toaster } from 'react-hot-toast';

// Dynamically import transformers only in browser
let pipeline: any = null;
let env: any = null;

export default function BrowserDemoPage() {
  const [captioner, setCaptioner] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [caption, setCaption] = useState<string | null>(null);
  const [inferenceTime, setInferenceTime] = useState<number | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Load transformers.js dynamically
  useEffect(() => {
    const loadTransformers = async () => {
      try {
        const transformers = await import('@xenova/transformers');
        pipeline = transformers.pipeline;
        env = transformers.env;
        
        // Configure
        env.allowLocalModels = false;
        env.useBrowserCache = true;
        
        console.log('✅ Transformers.js loaded');
      } catch (error) {
        console.error('Failed to load Transformers.js:', error);
        toast.error('Failed to load AI library');
      }
    };

    loadTransformers();
  }, []);

  // Load model
  const loadModel = async () => {
    if (!pipeline) {
      toast.error('Please wait for Transformers.js to load');
      return;
    }

    setIsLoading(true);
    setLoadingMessage('Downloading model...');
    setLoadingProgress(0);

    try {
      // Use Xenova/vit-gpt2 which has proper ONNX files for browser
      const model = await pipeline('image-to-text', 'Xenova/vit-gpt2-image-captioning', {
        progress_callback: (progress: any) => {
          if (progress.status === 'progress' && progress.progress !== undefined) {
            setLoadingProgress(Math.round(progress.progress));
            setLoadingMessage(`Downloading... ${Math.round(progress.progress)}%`);
          } else if (progress.status === 'done') {
            setLoadingMessage('Initializing model...');
          }
        }
      });

      setCaptioner(model);
      setIsLoading(false);
      setLoadingMessage('');
      toast.success('Model loaded successfully! 🎉');
    } catch (error) {
      console.error('Failed to load model:', error);
      setIsLoading(false);
      toast.error('Failed to load model');
    }
  };

  // Handle file upload
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error('Image must be less than 10MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string);
      setCaption(null);
      setInferenceTime(null);
      toast.success('Image loaded!');
    };
    reader.readAsDataURL(file);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp', '.gif'] },
    maxFiles: 1,
  });

  // Generate caption
  const generateCaption = async () => {
    if (!imagePreview) {
      toast.error('Please upload an image first');
      return;
    }

    if (!captioner) {
      toast.error('Please load the model first');
      return;
    }

    setIsGenerating(true);
    const startTime = performance.now();

    try {
      // Create an Image element from the preview URL
      const img = new Image();
      img.src = imagePreview;
      
      await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
      });

      // Generate caption using the image element
      const result = await captioner(img, {
        max_new_tokens: 50,
        num_beams: 5,
        do_sample: false,
      });

      const time = Math.round(performance.now() - startTime);
      const text = result[0]?.generated_text || result[0]?.text || 'No caption generated';

      setCaption(text);
      setInferenceTime(time);
      toast.success(`Caption generated in ${time}ms! 🎉`);
    } catch (error) {
      console.error('Caption generation failed:', error);
      toast.error('Failed to generate caption');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Toaster position="top-center" />
      
      {/* Header */}
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            🎨 Browser AI Image Captioning
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            100% Free • No API • No Limits • Complete Privacy
          </p>
        </div>

        {/* Status Badge */}
        <div className="flex justify-center gap-3 mb-8">
          <span className={`px-4 py-2 rounded-full text-sm font-semibold ${
            captioner 
              ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
              : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
          }`}>
            {captioner ? '✓ Model Ready' : '○ Model Not Loaded'}
          </span>
          <span className="px-4 py-2 rounded-full text-sm font-semibold bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
            🖥️ Browser Inference
          </span>
        </div>

        {/* Load Model Section */}
        {!captioner && !isLoading && (
          <div className="max-w-2xl mx-auto bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl mb-8">
            <h2 className="text-2xl font-bold mb-4">Step 1: Load AI Model</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Download the AI model once (~500MB). It will be cached in your browser for instant future use.
            </p>
            <button
              onClick={loadModel}
              className="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
            >
              Load AI Model
            </button>
          </div>
        )}

        {/* Loading Progress */}
        {isLoading && (
          <div className="max-w-2xl mx-auto bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl mb-8">
            <h2 className="text-2xl font-bold mb-4">Loading Model...</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">{loadingMessage}</p>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4">
              <div
                className="bg-gradient-to-r from-blue-600 to-purple-600 h-4 rounded-full transition-all duration-300 flex items-center justify-center text-xs text-white font-semibold"
                style={{ width: `${loadingProgress}%` }}
              >
                {loadingProgress > 10 && `${loadingProgress}%`}
              </div>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-4">
              This happens only once. The model will be cached for future use.
            </p>
          </div>
        )}

        {/* Upload & Caption Section */}
        {captioner && (
          <div className="max-w-4xl mx-auto space-y-8">
            {/* Upload Area */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl">
              <h2 className="text-2xl font-bold mb-4">Step 2: Upload Image</h2>
              
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
                  isDragActive
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
                }`}
              >
                <input {...getInputProps()} />
                {imagePreview ? (
                  <div className="space-y-4">
                    <img
                      src={imagePreview}
                      alt="Preview"
                      className="max-h-96 mx-auto rounded-lg shadow-lg"
                    />
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Click or drag to replace
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="text-6xl">📸</div>
                    <div>
                      <p className="text-xl font-semibold mb-2">Drop image here</p>
                      <p className="text-gray-600 dark:text-gray-400">or click to browse</p>
                      <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                        PNG, JPG, WEBP up to 10MB
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {imagePreview && (
                <button
                  onClick={generateCaption}
                  disabled={isGenerating}
                  className="mt-6 w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
                >
                  {isGenerating ? '🤖 Generating Caption...' : '✨ Generate Caption'}
                </button>
              )}
            </div>

            {/* Results */}
            {caption && (
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl">
                <h2 className="text-2xl font-bold mb-4">Generated Caption</h2>
                
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl p-6 mb-6">
                  <p className="text-2xl font-medium text-gray-800 dark:text-gray-200">
                    "{caption}"
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                    <div className="text-sm text-gray-600 dark:text-gray-400">Inference Time</div>
                    <div className="text-2xl font-bold">{inferenceTime}ms</div>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                    <div className="text-sm text-gray-600 dark:text-gray-400">Method</div>
                    <div className="text-2xl font-bold">Browser</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Features */}
        <div className="mt-16 grid md:grid-cols-4 gap-6 max-w-6xl mx-auto">
          <div className="text-center p-6">
            <div className="text-4xl mb-3">🖥️</div>
            <h3 className="font-semibold mb-2">Browser-Based</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">No server needed</p>
          </div>
          <div className="text-center p-6">
            <div className="text-4xl mb-3">💰</div>
            <h3 className="font-semibold mb-2">100% Free</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">No limits forever</p>
          </div>
          <div className="text-center p-6">
            <div className="text-4xl mb-3">🔒</div>
            <h3 className="font-semibold mb-2">Private</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Images stay local</p>
          </div>
          <div className="text-center p-6">
            <div className="text-4xl mb-3">⚡</div>
            <h3 className="font-semibold mb-2">Fast</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">1-5 second captions</p>
          </div>
        </div>
      </div>
    </div>
  );
}
