/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config, { isServer }) => {
    // Fixes for Transformers.js in Next.js
    config.resolve.alias = {
      ...config.resolve.alias,
      'sharp$': false,
      'onnxruntime-node$': false,
    };

    // Allow WebAssembly
    config.experiments = {
      ...config.experiments,
      asyncWebAssembly: true,
      layers: true,
    };

    // Ignore node-specific modules in browser
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        crypto: false,
      };
    }

    return config;
  },
  transpilePackages: ['@xenova/transformers'],
};

module.exports = nextConfig;
