import type { ReactNode } from "react";
import FundoLiquido from "./fundo-liquido";
import Icone from "./icone";

/** Moldura compartilhada de login/cadastro (#211): cartão translúcido sobre o fundo decorativo. */
export default function MolduraConta({ titulo, descricao, retorno, contexto, rotulo, children }: {
  titulo: string;
  descricao: string;
  retorno: string | null;
  contexto?: ReactNode;
  rotulo: string;
  children: ReactNode;
}) {
  return (
    <main className="auth-page flex flex-1 items-start justify-center px-4 py-10 sm:items-center sm:py-16">
      <FundoLiquido />
      <section className="auth-card flex min-w-0 flex-col gap-6" aria-label={rotulo}>
        <div>
          <span className="kicker">{retorno ? "Quase lá" : "Sua conta"}</span>
          <h1 className="mt-2 text-2xl font-medium tracking-tight sm:text-3xl">{titulo}</h1>
          <p className="mt-2 text-sm leading-relaxed text-(--ink-soft)">{descricao}</p>
        </div>
        {retorno && <p className="status-box success flex gap-3"><Icone nome="check" pequeno /><span><strong className="block font-medium">Você voltará para esta avaliação</strong>O endereço de retorno foi validado e será usado depois do acesso.</span></p>}
        {contexto}
        {children}
      </section>
    </main>
  );
}
