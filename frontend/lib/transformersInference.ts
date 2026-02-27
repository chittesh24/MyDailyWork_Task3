/**
 * Browser-based Image Captioning using Transformers.js
 * 100% Free, No API limits, Runs entirely in browser
 * Optimized for speed and accuracy
 */

// @ts-ignore - Transformers.js types
import { pipeline, env } from '@xenova/transformers';

// Configure for optimal performance
env.allowLocalModels = false;
env.useBrowserCache = true;
env.allowRemoteModels = true;

// Model configurations - ordered by speed/accuracy tradeoff
export const AVAILABLE_MODELS = {
  // Fastest - Good for real-time inference
  'vit-gpt2': {
    name: 'Salesforce/blip-image-captioning-base',
    task: 'image-to-text',
    speed: 'fast',
    accuracy: 'good',
    size: '~500MB',
    description: 'BLIP Base - Best balance of speed and quality'
  },
  // Best accuracy - Slightly slower but excellent results
  'blip-large': {
    name: 'Salesforce/blip-image-captioning-large', 
    task: 'image-to-text',
    speed: 'medium',
    accuracy: 'excellent',
    size: '~900MB',
    description: 'BLIP Large - Highest quality captions'
  },
  // Alternative fast model
  'git-base': {
    name: 'microsoft/git-base-coco',
    task: 'image-to-text', 
    speed: 'fast',
    accuracy: 'good',
    size: '~700MB',
    description: 'GIT Base - Fast and reliable'
  }
};

type ModelKey = keyof typeof AVAILABLE_MODELS;
type ProgressCallback = (progress: { status: string; progress?: number; model?: string }) => void;

class TransformersInference {
  private captioner: any = null;
  private currentModel: string | null = null;
  private loadingPromise: Promise<any> | null = null;
  private progressCallback: ProgressCallback | null = null;

  /**
   * Set progress callback for model loading updates
   */
  setProgressCallback(callback: ProgressCallback | null) {
    this.progressCallback = callback;
  }

  /**
   * Load the image captioning model (with caching)
   */
  async loadModel(modelKey: ModelKey = 'vit-gpt2', forceReload = false): Promise<void> {
    // Only run in browser environment
    if (typeof window === 'undefined') {
      console.warn('Model loading skipped - not in browser environment');
      return;
    }

    const modelConfig = AVAILABLE_MODELS[modelKey];
    
    // Return existing model if already loaded and same model
    if (this.captioner && this.currentModel === modelConfig.name && !forceReload) {
      console.log('✅ Model already loaded:', modelConfig.name);
      return;
    }

    // Return existing loading promise if in progress
    if (this.loadingPromise && this.currentModel === modelConfig.name) {
      console.log('⏳ Model loading in progress...');
      return this.loadingPromise;
    }

    // Start loading
    console.log('🚀 Loading model:', modelConfig.name);
    this.progressCallback?.({ status: 'downloading', model: modelConfig.name });

    this.loadingPromise = pipeline('image-to-text', modelConfig.name, {
      progress_callback: (progress: any) => {
        console.log('Download progress:', progress);
        if (progress.status === 'progress' && progress.progress !== undefined) {
          this.progressCallback?.({
            status: 'downloading',
            progress: Math.round(progress.progress),
            model: modelConfig.name
          });
        } else if (progress.status === 'done') {
          this.progressCallback?.({
            status: 'loading',
            model: modelConfig.name
          });
        }
      }
    });

    try {
      this.captioner = await this.loadingPromise;
      this.currentModel = modelConfig.name;
      console.log('✅ Model loaded successfully:', modelConfig.name);
      this.progressCallback?.({ status: 'ready', model: modelConfig.name });
    } catch (error) {
      console.error('❌ Failed to load model:', error);
      this.progressCallback?.({ status: 'error', model: modelConfig.name });
      throw error;
    } finally {
      this.loadingPromise = null;
    }
  }

  /**
   * Generate caption for an image
   */
  async generateCaption(
    imageUrl: string,
    options: {
      modelKey?: ModelKey;
      maxLength?: number;
      numBeams?: number;
      temperature?: number;
    } = {}
  ): Promise<{
    caption: string;
    confidence?: number;
    inferenceTime: number;
    model: string;
    method: string;
  }> {
    // Only run in browser environment
    if (typeof window === 'undefined') {
      throw new Error('Transformers.js inference only available in browser');
    }

    const {
      modelKey = 'vit-gpt2',
      maxLength = 50,
      numBeams = 5,
      temperature = 1.0
    } = options;

    // Ensure model is loaded
    await this.loadModel(modelKey);

    if (!this.captioner) {
      throw new Error('Model not loaded');
    }

    const startTime = performance.now();

    try {
      // Generate caption
      const result = await this.captioner(imageUrl, {
        max_new_tokens: maxLength,
        num_beams: numBeams,
        temperature: temperature,
        do_sample: false, // Deterministic for best quality
      });

      const inferenceTime = performance.now() - startTime;

      // Extract caption text
      const caption = Array.isArray(result) 
        ? result[0]?.generated_text || result[0]?.text || ''
        : result?.generated_text || result?.text || '';

      console.log('✅ Caption generated:', caption, `(${inferenceTime.toFixed(0)}ms)`);

      return {
        caption: caption.trim(),
        inferenceTime: Math.round(inferenceTime),
        model: this.currentModel || 'unknown',
        method: 'transformers_js_browser',
        confidence: result[0]?.score
      };
    } catch (error) {
      console.error('❌ Caption generation failed:', error);
      throw error;
    }
  }

  /**
   * Generate multiple captions with different parameters
   */
  async generateMultipleCaptions(
    imageUrl: string,
    count: number = 3,
    modelKey: ModelKey = 'vit-gpt2'
  ): Promise<Array<{ caption: string; confidence?: number }>> {
    // Only run in browser environment
    if (typeof window === 'undefined') {
      throw new Error('Transformers.js inference only available in browser');
    }

    await this.loadModel(modelKey);

    if (!this.captioner) {
      throw new Error('Model not loaded');
    }

    const results = await this.captioner(imageUrl, {
      max_new_tokens: 50,
      num_beams: 5,
      num_return_sequences: count,
      do_sample: true,
      temperature: 0.8,
    });

    return Array.isArray(results) 
      ? results.map((r: any) => ({
          caption: (r.generated_text || r.text || '').trim(),
          confidence: r.score
        }))
      : [{ caption: (results.generated_text || results.text || '').trim() }];
  }

  /**
   * Check if model is loaded
   */
  isModelLoaded(): boolean {
    return this.captioner !== null;
  }

  /**
   * Get current model info
   */
  getCurrentModel(): string | null {
    return this.currentModel;
  }

  /**
   * Unload model to free memory
   */
  async unloadModel(): Promise<void> {
    this.captioner = null;
    this.currentModel = null;
    this.loadingPromise = null;
    console.log('🗑️ Model unloaded');
  }
}

// Singleton instance
const transformersInference = new TransformersInference();

export default transformersInference;
export type { ModelKey, ProgressCallback };
