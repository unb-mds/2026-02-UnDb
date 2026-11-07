import type { Metadata } from "next";
import Cabecalho from "@/components/cabecalho";
import AvisoAgradecimento from "@/components/aviso-agradecimento";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "UnDb — escolha com quem aprender",
  description: "Consulta pública de avaliações estruturadas de professores e disciplinas da UnB.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="pt-BR" className="dark h-full antialiased">
      <body className="min-h-full flex flex-col">
        <a href="#conteudo" className="skip-link">Pular para o conteúdo</a>
        <Cabecalho />
        <div className="simulation-banner" role="note"><div className="container"><strong>Ambiente de visualização</strong><span>Catálogo institucional real · avaliações e comentários simulados, sem representar opiniões reais sobre os docentes.</span></div></div>
        <AvisoAgradecimento />
        <div id="conteudo" className="app-content">{children}</div>
        <footer className="footer"><div className="container footer-inner"><span>UnDb · Grupo 7 · UnB 2026/2</span><div><Link href="/estados">Estados da exibição</Link><Link href="/moderacao">Moderação</Link><span className="demo-label">Catálogo real · avaliações simuladas</span></div></div></footer>
      </body>
    </html>
  );
}
