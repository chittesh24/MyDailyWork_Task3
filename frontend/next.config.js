/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@xenova/transformers'],

  webpack: (config, { isServer }) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      sharp: false,
      'onnxruntime-node': false,
    }

    config.experiments = {
      ...config.experiments,
      asyncWebAssembly: true,
      layers: true,
    }

    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        crypto: false,
      }
    }

    return config
  },

  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Cross-Origin-Opener-Policy',
            value: 'same-origin',
          },
          {
            key: 'Cross-Origin-Embedder-Policy',
            value: 'require-corp',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig