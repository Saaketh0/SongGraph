import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  webpack(config) {
    config.resolve = config.resolve ?? {};
    config.resolve.alias = config.resolve.alias ?? {};
    // Cosmograph package internals import via "@/...", so keep this alias scoped for its runtime.
    config.resolve.alias["@"] = path.resolve(process.cwd(), "node_modules/@cosmograph/cosmograph");
    return config;
  },
};

export default nextConfig;
