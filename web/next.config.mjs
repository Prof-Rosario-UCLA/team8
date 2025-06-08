/** @type {import('next').NextConfig} */
const nextConfig = {
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

export default nextConfig; 