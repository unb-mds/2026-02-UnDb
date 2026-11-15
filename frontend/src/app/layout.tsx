import type { Metadata } from "next";
import { metadadosCompartilhamento } from "@/lib/metadados-compartilhamento";
import TransicaoPagina from "@/components/transicao-pagina";
import Rodape from "@/components/rodape";
import Cabecalho from "@/components/cabecalho";
import AvisoAgradecimento from "@/components/aviso-agradecimento";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = metadadosCompartilhamento;

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="pt-BR"
      className={`${geistSans.variable} ${geistMono.variable} dark h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <a href="#conteudo" className="skip-link">Pular para o conteúdo</a>
        <Cabecalho />
        <AvisoAgradecimento />
        <TransicaoPagina>{children}</TransicaoPagina>
        <Rodape />
      </body>
    </html>
  );
}
