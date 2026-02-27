/**
 * React Hook for Image Captioning with Transformers.js
 * Provides easy-to-use interface for browser-based inference
 */

import { useState, useCallback, useEffect } from 'react';
import transformersInference, { ModelKey, AVAILABLE_MODELS } from '@/lib/transformersInference';
import axios from 'axios';

interface CaptionResult {
  caption: string;
  inferenceTime: number;
  model: string;
  method: 'browser' | 'api';
  confidence?: number;
}

interface LoadingState {
  status: 'idle' | 'loading-model' | 'generating' | 'ready' | 'error';
  progress?: number;
  message?: string;
}

interface UseImageCaptioningOptions {
  defaultModel?: ModelKey;
  autoLoadModel?: boolean;
  fallbackToAPI?: boolean;
  apiEndpoint?: string;
}

export function useImageCaptioning(options: UseImageCaptioningOptions = {}) {
  const {
    defaultModel = 'vit-gpt2',
    autoLoadModel = false,
    fallbackToAPI = true,
    apiEndpoint = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  } = options;

  const [loadingState, setLoadingState] = useState<LoadingState>({ status: 'idle' });
  const [currentModel, setCurrentModel] = useState<ModelKey>(defaultModel);
  const [isModelLoaded, setIsModelLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Setup progress callback
  useEffect(() => {
    transformersInference.setProgressCallback((progress) => {
      if (progress.status === 'downloading') {
        setLoadingState({
          status: 'loading-model',
          progress: progress.progress,
          message: `Downloading model... ${progress.progress || 0}%`
        });
      } else if (progress.status === 'loading') {
        setLoadingState({
          status: 'loading-model',
          message: 'Initializing model...'
        });
      } else if (progress.status === 'ready') {
        setLoadingState({ status: 'ready', message: 'Model ready!' });
        setIsModelLoaded(true);
      } else if (progress.status === 'error') {
        setLoadingState({ status: 'error', message: 'Failed to load model' });
        setError('Failed to load model');
      }
    });

    return () => {
      transformersInference.setProgressCallback(null);
    };
  }, []);

  // Auto-load model on mount if requested
  useEffect(() => {
    if (autoLoadModel) {
      loadModel(defaultModel);
    }
  }, [autoLoadModel, defaultModel]);

  /**
   * Load the captioning model
   */
  const loadModel = useCallback(async (modelKey: ModelKey = defaultModel) => {
    try {
      setLoadingState({ status: 'loading-model', message: 'Loading model...' });
      setError(null);
      setCurrentModel(modelKey);
      
      await transformersInference.loadModel(modelKey);
      
      setIsModelLoaded(true);
      setLoadingState({ status: 'ready', message: 'Model loaded!' });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load model';
      setError(errorMessage);
      setLoadingState({ status: 'error', message: errorMessage });
      setIsModelLoaded(false);
      throw err;
    }
  }, [defaultModel]);

  /**
   * Generate caption using browser-based inference
   */
  const generateCaptionBrowser = useCallback(async (
    imageUrl: string,
    options: {
      modelKey?: ModelKey;
      maxLength?: number;
      numBeams?: number;
    } = {}
  ): Promise<CaptionResult> => {
    try {
      setLoadingState({ status: 'generating', message: 'Generating caption...' });
      setError(null);

      const result = await transformersInference.generateCaption(imageUrl, {
        modelKey: options.modelKey || currentModel,
        maxLength: options.maxLength,
        numBeams: options.numBeams
      });

      setLoadingState({ status: 'ready', message: 'Caption generated!' });

      return {
        caption: result.caption,
        inferenceTime: result.inferenceTime,
        model: result.model,
        method: 'browser',
        confidence: result.confidence
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate caption';
      setError(errorMessage);
      setLoadingState({ status: 'error', message: errorMessage });
      throw err;
    }
  }, [currentModel]);

  /**
   * Generate caption using API fallback
   */
  const generateCaptionAPI = useCallback(async (
    imageFile: File
  ): Promise<CaptionResult> => {
    try {
      setLoadingState({ status: 'generating', message: 'Generating caption via API...' });
      setError(null);

      const formData = new FormData();
      formData.append('file', imageFile);

      const response = await axios.post(
        `${apiEndpoint}/api/v1/caption`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setLoadingState({ status: 'ready', message: 'Caption generated!' });

      return {
        caption: response.data.caption,
        inferenceTime: response.data.inference_time_ms || 0,
        model: response.data.model_version || 'API',
        method: 'api'
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'API request failed';
      setError(errorMessage);
      setLoadingState({ status: 'error', message: errorMessage });
      throw err;
    }
  }, [apiEndpoint]);

  /**
   * Smart caption generation - tries browser first, falls back to API
   */
  const generateCaption = useCallback(async (
    input: string | File,
    options: {
      modelKey?: ModelKey;
      maxLength?: number;
      numBeams?: number;
      preferBrowser?: boolean;
    } = {}
  ): Promise<CaptionResult> => {
    const { preferBrowser = true } = options;

    // Check if input is a File (works in both browser and SSR)
    const isFile = typeof input === 'object' && input !== null && 'name' in input && 'type' in input;

    // If browser inference is preferred and available
    if (preferBrowser && typeof input === 'string') {
      try {
        // Ensure model is loaded
        if (!isModelLoaded) {
          await loadModel(options.modelKey || currentModel);
        }
        return await generateCaptionBrowser(input, options);
      } catch (browserError) {
        console.error('Browser inference failed:', browserError);
        
        // Fallback to API if enabled
        if (fallbackToAPI && isFile) {
          console.log('Falling back to API...');
          return await generateCaptionAPI(input as File);
        }
        throw browserError;
      }
    }

    // Use API for File inputs or when browser is not preferred
    if (isFile) {
      return await generateCaptionAPI(input as File);
    }

    throw new Error('Invalid input type');
  }, [isModelLoaded, currentModel, fallbackToAPI, loadModel, generateCaptionBrowser, generateCaptionAPI]);

  /**
   * Generate multiple captions for comparison
   */
  const generateMultipleCaptions = useCallback(async (
    imageUrl: string,
    count: number = 3
  ): Promise<Array<{ caption: string; confidence?: number }>> => {
    try {
      setLoadingState({ status: 'generating', message: 'Generating multiple captions...' });
      setError(null);

      if (!isModelLoaded) {
        await loadModel(currentModel);
      }

      const results = await transformersInference.generateMultipleCaptions(
        imageUrl,
        count,
        currentModel
      );

      setLoadingState({ status: 'ready', message: 'Captions generated!' });
      return results;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate captions';
      setError(errorMessage);
      setLoadingState({ status: 'error', message: errorMessage });
      throw err;
    }
  }, [isModelLoaded, currentModel, loadModel]);

  /**
   * Switch to a different model
   */
  const switchModel = useCallback(async (modelKey: ModelKey) => {
    await loadModel(modelKey);
  }, [loadModel]);

  /**
   * Unload model to free memory
   */
  const unloadModel = useCallback(async () => {
    await transformersInference.unloadModel();
    setIsModelLoaded(false);
    setLoadingState({ status: 'idle' });
    setCurrentModel(defaultModel);
  }, [defaultModel]);

  return {
    // State
    loadingState,
    isModelLoaded,
    currentModel,
    error,
    availableModels: AVAILABLE_MODELS,

    // Actions
    loadModel,
    generateCaption,
    generateMultipleCaptions,
    switchModel,
    unloadModel,

    // Advanced
    generateCaptionBrowser,
    generateCaptionAPI,
  };
}

export type { CaptionResult, LoadingState, ModelKey };
