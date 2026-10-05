/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  outputFileTracingIncludes: {
    '/api/artifact': ['../output/**/*', '../reports/**/*']
  },
  experimental: {
    externalDir: true
  }
};

export default nextConfig;
