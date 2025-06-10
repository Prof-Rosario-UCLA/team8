import serwist from "@serwist/next";

/** @type {import('next').NextConfig} */
export const nextConfig = {
  reactStrictMode: true,
  // Add or modify the rewrites configuration
  async rewrites() {
    const baseUrl = process.env.SERVER_URL || 'http://127.0.0.1:5001';
  
    return [
      {
        source: '/api/:path*',
        // Proxy to the Flask app (5001 in our scripts)
        destination: baseUrl + '/api/:path*',
      },
    ];
  },
  // Force headers to not cache
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-store, no-cache, must-revalidate, proxy-revalidate',
          },
          { key: 'Pragma', value: 'no-cache' },
          { key: 'Expires', value: '0' },
        ],
      },
    ];
  },
};

const withSerwist = serwist({
  swSrc: "src/app/sw.ts",
  swDest: "public/sw.js",
  cacheOnNavigation: true,
  reloadOnOnline: true,
  disable: process.env.NODE_ENV === "development",
});

export default withSerwist(nextConfig); 