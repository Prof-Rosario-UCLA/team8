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
};

const withSerwist = serwist({
  swSrc: "src/app/sw.ts",
  swDest: "public/sw.js",
  cacheOnNavigation: true,
  reloadOnOnline: true,
  disable: process.env.NODE_ENV === "development",
});

export default withSerwist(nextConfig); 