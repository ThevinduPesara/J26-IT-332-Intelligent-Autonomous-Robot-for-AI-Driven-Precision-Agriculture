import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "127.0.0.1", port: "8000", pathname: "/**" },
      { protocol: "http", hostname: "127.0.0.1", port: "8001", pathname: "/**" },
      { protocol: "http", hostname: "127.0.0.1", port: "8002", pathname: "/**" },
      { protocol: "http", hostname: "127.0.0.1", port: "8003", pathname: "/**" },
      { protocol: "http", hostname: "localhost", port: "8000", pathname: "/**" },
      { protocol: "http", hostname: "localhost", port: "8001", pathname: "/**" },
      { protocol: "http", hostname: "localhost", port: "8002", pathname: "/**" },
      { protocol: "http", hostname: "localhost", port: "8003", pathname: "/**" },
    ],
  },
  allowedDevOrigins: ["localhost", "127.0.0.1", "192.168.140.1", "192.168.*.*"],
  cacheComponents: true,
  partialPrefetching: true,
  reactCompiler: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
