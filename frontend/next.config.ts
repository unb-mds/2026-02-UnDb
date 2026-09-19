import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // O Docker empacota o servidor mínimo; o fluxo local mantém next start.
  output: process.env.BUILD_STANDALONE === "true" ? "standalone" : undefined,
};

export default nextConfig;
