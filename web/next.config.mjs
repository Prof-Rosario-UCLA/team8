/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Add or modify the rewrites configuration
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        // Proxy to the Flask app (5001 in our scripts)
        destination: 'http://127.0.0.1:5001/api/:path*',
      },
    ];
  },
};

export default nextConfig; 