import type { ReactNode } from "react";
import Image from "next/image";
import Link from "next/link";
import FundoLiquido from "./fundo-liquido";
import Icone from "./icone";

/** Moldura compartilhada de login/cadastro (#211): cartão translúcido sobre o fundo decorativo. */
export default function MolduraConta({ titulo, descricao, retorno, contexto, opcoes, rotulo, ampla = false, children }: {
  ampla?: boolean;
  titulo: string;
  descricao: string;
  retorno: string | null;
  contexto?: ReactNode;
  opcoes?: ReactNode;
  rotulo: string;
  children: ReactNode;
}) {
  return (
    <main className="auth-page flex flex-1 items-start justify-center px-4 py-10 sm:items-center sm:py-16">
      <FundoLiquido />
      <section className={`auth-card flex min-w-0 flex-col gap-5 ${ampla ? "w-full! max-w-5xl" : ""}`} aria-label={rotulo}>
        <Link href="/" aria-label="UnDb — início" className="mb-1 inline-flex min-h-11 w-fit items-center">
          <Image src="/brand/undb-logo.png" alt="" width={600} height={201} className="h-auto w-28" loading="eager" />
        </Link>
        <div>
          <span className="kicker">Sua conta</span>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">{titulo}</h1>
          <p className="mt-2 text-sm leading-relaxed text-(--ink-soft)">{descricao}</p>
        </div>
        {opcoes}
        {retorno && <p className="status-box success flex items-start gap-3"><Icone nome="check" pequeno /><span>Você voltará para esta avaliação depois do acesso. Para enviar, confirme seu e-mail e revise suas respostas.</span></p>}
        {contexto}
        {children}
        {retorno && <Link href={retorno} className="back-link"><Icone nome="arrow-left" pequeno />Voltar à avaliação</Link>}
      </section>
    </main>
  );
}
