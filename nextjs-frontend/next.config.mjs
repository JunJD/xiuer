import ForkTsCheckerWebpackPlugin from 'fork-ts-checker-webpack-plugin';

/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    // 关闭图片优化
    unoptimized: true,
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.plugins.push(
        new ForkTsCheckerWebpackPlugin({
          async: true, // Run type checking synchronously to block the build
          typescript: {
            configOverwrite: {
              compilerOptions: {
                skipLibCheck: true,
              },
            },
          },
        })
      );
    }
    return config;
  },
  output: 'standalone',
  experimental: {
    //
  },
  async rewrites() {
    // In development, proxy API requests to the backend service
    if (process.env.NODE_ENV === "development") {
      return [
        {
          source: "/api/:path*",
          destination: "http://backend:8000/api/:path*", // Proxy to Backend
        },
        {
          source: "/auth/:path*",
          destination: "http://backend:8000/auth/:path*", // Proxy to Backend
        },
        {
          source: "/docs",
          destination: "http://backend:8000/docs", // Proxy to Backend
        },
        {
          source: "/openapi.json",
          destination: "http://backend:8000/openapi.json", // Proxy to Backend
        },
      ];
    }
    return [];
  },
};

export default nextConfig;