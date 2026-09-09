/** @type {import('next').NextConfig} */
const rawApiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const apiBase = rawApiBase.replace(/\/+$/, "");

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${apiBase}/api/v1/:path*`,
      },
      {
        source: "/health",
        destination: `${apiBase}/health`,
      },
    ];
  },
};

export default nextConfig;
