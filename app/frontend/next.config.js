/** @type {import('next').NextConfig} */
const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

function normalizeApiBaseUrl(value) {
  const trimmed = String(value || "").trim().replace(/\/+$/, "");
  if (!trimmed) return "https://eduboost-api.onrender.com/api/v2";
  return trimmed.endsWith("/api/v2") ? trimmed : `${trimmed}/api/v2`;
}

const apiBaseUrl = normalizeApiBaseUrl(process.env.NEXT_PUBLIC_API_URL);

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  outputFileTracingRoot: __dirname,
  // PPR remains disabled — re-evaluate after stable Next.js support (FE-SPIKE-003)
  // experimental: { ppr: true }, // DO NOT ENABLE
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

module.exports = withBundleAnalyzer(nextConfig);
