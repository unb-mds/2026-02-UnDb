import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async headers() {
    return ["/contato", "/atendimento", "/confirmar-email", "/redefinir-senha"].map(source => ({ source, headers: [
      { key: "Cache-Control", value: "no-store" },
      { key: "Referrer-Policy", value: "no-referrer" },
    ] }));
  },
  // Metadados no head inicial, inclusive para crawlers de compartilhamento.
  htmlLimitedBots: /.*/,
  // O Docker empacota o servidor mínimo; o fluxo local mantém next start.
  output: process.env.BUILD_STANDALONE === "true" ? "standalone" : undefined,
};

export default nextConfig;
