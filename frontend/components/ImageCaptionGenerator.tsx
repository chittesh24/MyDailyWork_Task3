/**
 * Image Caption Generator Component
 * Uses Transformers.js for 100% free browser-based inference
 */

'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useImageCaptioning } from '../hooks/useImageCaptioning';
import type { ModelKey } from '../lib/transformersInference';
import toast from 'react-hot-toast';

export default function ImageCaptionGenerator() {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [caption, setCaption] = useState<string | null>(null);
  const [inferenceTime, setInferenceTime] = useState<number | null>(null);
  const [method, setMethod] = useState<'browser' | 'api' | null>(null);

  const {
    loadingState,
    isModelLoaded,
    currentModel,
    availableModels,
    error,
    loadModel,
    generateCaption,
    switchModel,
  } = useImageCaptioning({
    defaultModel: 'vit-gpt2',
    autoLoadModel: false,
    fallbackToAPI: true,
  });

  // Handle image drop/upload
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Image size must be less than 10MB');
      return;
    }

    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
    setCaption(null);
    setInferenceTime(null);
    setMethod(null);
    
    toast.success('Image loaded! Ready to generate caption.');
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp', '.gif']
    },
    maxFiles: 1,
    multiple: false,
  });

  // Generate caption
  const handleGenerateCaption = async () => {
    if (!imagePreview) {
      toast.error('Please upload an image first');
      return;
    }

    try {
      // Load model if not loaded
      if (!isModelLoaded) {
        toast.loading('Loading model for the first time... (this may take a minute)', {
          id: 'model-loading',
        });
      }

      const result = await generateCaption(imagePreview, {
        modelKey: currentModel,
        maxLength: 50,
        numBeams: 5,
        preferBrowser: true,
      });

      setCaption(result.caption);
      setInferenceTime(result.inferenceTime);
      setMethod(result.method);

      toast.dismiss('model-loading');
      toast.success(`Caption generated in ${result.inferenceTime}ms!`);
    } catch (err) {
      toast.dismiss('model-loading');
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate caption';
      toast.error(errorMessage);
      console.error('Caption generation error:', err);
    }
  };

  // Handle model change
  const handleModelChange = async (modelKey: ModelKey) => {
    try {
      toast.loading('Switching model...', { id: 'model-switch' });
      await switchModel(modelKey);
      toast.dismiss('model-switch');
      toast.success(`Switched to ${availableModels[modelKey].description}`);
    } catch (err) {
      toast.dismiss('model-switch');
      toast.error('Failed to switch model');
    }
  };

  // Manual model load
  const handleLoadModel = async () => {
    try {
      toast.loading('Loading model...', { id: 'manual-load' });
      await loadModel(currentModel);
      toast.dismiss('manual-load');
      toast.success('Model loaded successfully!');
    } catch (err) {
      toast.dismiss('manual-load');
      toast.error('Failed to load model');
    }
  };

  const isGenerating = loadingState.status === 'generating';
  const isLoadingModel = loadingState.status === 'loading-model';

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          AI Image Captioning
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          100% Free • No API Limits • Runs in Your Browser
        </p>
        <div className="flex items-center justify-center gap-2 text-sm">
          <span className={`px-3 py-1 rounded-full ${
            isModelLoaded 
              ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
              : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
          }`}>
            {isModelLoaded ? '✓ Model Ready' : '○ Model Not Loaded'}
          </span>
          {method && (
            <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
              {method === 'browser' ? '🖥️ Browser Inference' : '☁️ API Inference'}
            </span>
          )}
        </div>
      </div>

      {/* Model Selector */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
        <h2 className="text-xl font-semibold mb-4">Model Selection</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(availableModels).map(([key, model]) => (
            <button
              key={key}
              onClick={() => handleModelChange(key as ModelKey)}
              disabled={isLoadingModel || isGenerating}
              className={`p-4 rounded-lg border-2 transition-all ${
                currentModel === key
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-blue-300'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <div className="font-semibold text-sm mb-1">{model.description}</div>
              <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <div>Speed: {model.speed}</div>
                <div>Quality: {model.accuracy}</div>
                <div>Size: {model.size}</div>
              </div>
            </button>
          ))}
        </div>
        
        {!isModelLoaded && (
          <button
            onClick={handleLoadModel}
            disabled={isLoadingModel}
            className="mt-4 w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoadingModel ? 'Loading Model...' : 'Load Model'}
          </button>
        )}

        {/* Loading Progress */}
        {isLoadingModel && loadingState.progress !== undefined && (
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-2">
              <span>{loadingState.message}</span>
              <span>{loadingState.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${loadingState.progress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Image Upload */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
        <h2 className="text-xl font-semibold mb-4">Upload Image</h2>
        
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
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
                Click or drag to replace image
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <svg
                className="mx-auto h-16 w-16 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <div className="text-gray-600 dark:text-gray-400">
                <p className="text-lg font-semibold">Drop your image here</p>
                <p className="text-sm">or click to browse</p>
                <p className="text-xs mt-2">PNG, JPG, WEBP up to 10MB</p>
              </div>
            </div>
          )}
        </div>

        {imagePreview && (
          <button
            onClick={handleGenerateCaption}
            disabled={isGenerating || isLoadingModel}
            className="mt-6 w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold text-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
          >
            {isGenerating ? 'Generating Caption...' : 'Generate Caption'}
          </button>
        )}
      </div>

      {/* Results */}
      {caption && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg space-y-4">
          <h2 className="text-xl font-semibold">Generated Caption</h2>
          
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-6">
            <p className="text-2xl font-medium text-gray-800 dark:text-gray-200">
              "{caption}"
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3">
              <div className="text-gray-600 dark:text-gray-400">Inference Time</div>
              <div className="text-lg font-semibold">{inferenceTime}ms</div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3">
              <div className="text-gray-600 dark:text-gray-400">Method</div>
              <div className="text-lg font-semibold capitalize">{method}</div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3">
              <div className="text-gray-600 dark:text-gray-400">Model</div>
              <div className="text-lg font-semibold">{availableModels[currentModel].speed}</div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3">
              <div className="text-gray-600 dark:text-gray-400">Quality</div>
              <div className="text-lg font-semibold capitalize">{availableModels[currentModel].accuracy}</div>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200 font-semibold">Error</p>
          <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
}
