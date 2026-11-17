import type { Metadata } from "next";
import { metadadosCompartilhamento } from "./metadados-compartilhamento";

export const ORIGEM_SITE = "https://undb.app.br";
export const URLS_PUBLICAS = ["/", "/sobre", "/professores", "/disciplinas", "/privacidade", "/termos-de-uso"];
export const TAMANHO_SITEMAP = 5000;
export const TAMANHO_CATALOGO = 100;

export function urlPublica(caminho: string): string {
  if (!caminho.startsWith("/") || caminho.startsWith("//") || /[?#\\\x00-\x1f]/.test(caminho)) {
    throw new Error("URL pública deve ser um caminho canônico sem parâmetros.");
  }
  return new URL(caminho, ORIGEM_SITE).href;
}

export function metadadosPagina(titulo: string, descricao: string, caminho: string, indexar = true): Metadata {
  const url = urlPublica(caminho);
  return {
    title: titulo, description: descricao,
    alternates: { canonical: url },
    robots: { index: indexar, follow: true },
    openGraph: { ...metadadosCompartilhamento.openGraph, title: titulo, description: descricao, url },
    twitter: { ...metadadosCompartilhamento.twitter, title: titulo, description: descricao },
  };
}

export function xmlUrls(urls: string[], indice = false): string {
  const tag = indice ? "sitemap" : "url";
  const root = indice ? "sitemapindex" : "urlset";
  const escapar = (s: string) => s.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&apos;");
  return `<?xml version="1.0" encoding="UTF-8"?><${root} xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls.map(url => `<${tag}><loc>${escapar(url)}</loc></${tag}>`).join("")}</${root}>`;
}
