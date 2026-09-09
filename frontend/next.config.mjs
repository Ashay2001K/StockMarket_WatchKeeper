/** @type {import('next').NextConfig} */
const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
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
