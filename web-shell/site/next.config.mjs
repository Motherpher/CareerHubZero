/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  outputFileTracingIncludes: {
    '/api/artifact': ['./.careerhub-artifacts/**/*']
  },
  experimental: {
    externalDir: true
  }
};

export default nextConfig;
