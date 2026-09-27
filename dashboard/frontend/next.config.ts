import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // Silence the Turbopack "multiple lockfiles / wrong workspace root" warning.
  // `turbopack` is the correct top-level key in Next.js 15+ / 16.x.
  turbopack: {
    root: path.resolve(__dirname),
  },
};

export default nextConfig;
