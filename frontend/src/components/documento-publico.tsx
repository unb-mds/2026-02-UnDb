import Link from "next/link";
import type { ReactNode } from "react";
import { DOCUMENTOS_DATA, TERMOS_VERSAO } from "@/lib/termos";

export type SecaoDocumento = { id: string; titulo: string; conteudo: ReactNode };

export default function DocumentoPublico({ titulo, resumo, secoes }: {
  titulo: string; resumo: string; secoes: SecaoDocumento[];
}) {
  return <main className="mx-auto w-full max-w-4xl min-w-0 px-4 py-10 sm:px-6 sm:py-14">
    <p className="text-sm font-medium text-accent">Transparência do UnDb</p>
    <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-5xl">{titulo}</h1>
    <p className="mt-4 text-sm text-(--muted)">Versão {TERMOS_VERSAO} · Atualizado em <time dateTime={TERMOS_VERSAO}>{DOCUMENTOS_DATA}</time></p>
    <p className="mt-5 text-base leading-relaxed text-(--ink-soft)">{resumo}</p>
    <nav aria-label={`Seções de ${titulo}`} className="my-8 rounded-2xl border border-(--border) bg-(--panel) p-5">
      <ul className="grid gap-2 sm:grid-cols-2">{secoes.map(secao => <li key={secao.id}><Link href={`#${secao.id}`} className="inline-flex min-h-11 items-center text-sm text-accent underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent">{secao.titulo}</Link></li>)}</ul>
    </nav>
    <div className="space-y-10">{secoes.map(secao => <section key={secao.id} id={secao.id} aria-labelledby={`${secao.id}-titulo`} className="scroll-mt-48">
      <h2 id={`${secao.id}-titulo`} className="text-xl font-semibold sm:text-2xl">{secao.titulo}</h2>
      <div className="mt-4 space-y-4 text-base leading-relaxed wrap-break-word text-(--ink-soft) [&_a]:text-accent [&_a]:underline [&_a]:underline-offset-4 [&_a]:focus-visible:outline-2 [&_a]:focus-visible:outline-offset-4 [&_li]:pl-1 [&_ul]:list-disc [&_ul]:space-y-2 [&_ul]:pl-6">{secao.conteudo}</div>
    </section>)}</div>
    <nav aria-label="Documentos e contato" className="mt-12 flex flex-wrap gap-x-6 gap-y-3 border-t border-(--border) pt-6 text-sm">
      <Link href="/sobre" className="link">Sobre e metodologia</Link>
      <Link href="/privacidade" className="link">Política de Privacidade</Link>
      <Link href="/termos-de-uso" className="link">Termos de Uso</Link>
      <Link href="/contato" className="link">Contato e solicitações</Link>
    </nav>
  </main>;
}
