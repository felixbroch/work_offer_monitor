/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  async rewrites() {
    // Only use rewrites in development
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/backend/:path*',
          destination: process.env.BACKEND_URL || 'http://localhost:5000/api/:path*',
        },
      ]
    }
    // In production (Vercel), no rewrites needed - requests go directly to serverless functions
    return []
  },
}

module.exports = nextConfig
