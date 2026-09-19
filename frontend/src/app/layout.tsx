import type { Metadata } from "next";
import Link from "next/link";
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

export const metadata: Metadata = {
  title: "Avaliação de Professores UnB",
  description: "Consulta pública de avaliações estruturadas de professores e disciplinas da UnB.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="pt-BR"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <header className="border-b border-foreground/10">
          <div className="mx-auto flex w-full max-w-5xl flex-wrap items-center justify-between gap-x-6 gap-y-2 px-4 py-3">
            <Link href="/" aria-label="UnDb — início" className="py-2 text-xl font-semibold text-accent">
              UnDb
            </Link>
            <nav aria-label="Navegação principal" className="flex flex-wrap gap-x-4 gap-y-2 text-sm font-medium">
              <Link href="/professores" className="py-2 hover:text-accent hover:underline underline-offset-4">
                Professores
              </Link>
              <Link href="/disciplinas" className="py-2 hover:text-accent hover:underline underline-offset-4">
                Disciplinas
              </Link>
            </nav>
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}
