/** @type {import('next').NextConfig} */
function normalizeApiBaseUrl(value) {
  const trimmed = String(value || "").trim().replace(/\/+$/, "");
  if (!trimmed) return "https://eduboost-api.onrender.com/api/v2";
  return trimmed.endsWith("/api/v2") ? trimmed : `${trimmed}/api/v2`;
}

const apiBaseUrl = normalizeApiBaseUrl(process.env.NEXT_PUBLIC_API_URL);

const nextConfig = {
  output: 'standalone',
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: "/api/v2/:path*",
        destination: `${apiBaseUrl}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
