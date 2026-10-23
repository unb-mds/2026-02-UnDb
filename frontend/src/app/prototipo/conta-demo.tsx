"use client";

import Link from "next/link";
import { createContext, useContext, useState, type ReactNode } from "react";
import { useSearchParams } from "next/navigation";

type EstadoConta = "visitante" | "pendente" | "confirmada";
type ContaDemo = { estado: EstadoConta; alterarEstado: (estado: EstadoConta) => void };
const ContextoContaDemo = createContext<ContaDemo | null>(null);

export function ContaDemoProvider({ children }: { children: ReactNode }) {
  // Somente cenário visual em memória; não representa sessão e reinicia ao recarregar.
  const [estado, alterarEstado] = useState<EstadoConta>("visitante");
  return <ContextoContaDemo.Provider value={{ estado, alterarEstado }}>{children}</ContextoContaDemo.Provider>;
}

export function useContaDemo() {
  const conta = useContext(ContextoContaDemo);
  if (!conta) throw new Error("A conta demonstrativa só está disponível no protótipo.");
  return conta;
}

export function CabecalhoPrototipo() {
  const { estado } = useContaDemo();
  const consulta = useSearchParams();
  const parametros = new URLSearchParams(consulta.toString());
  if (parametros.get("etapa") !== "acesso") parametros.set("retornoEtapa", parametros.get("etapa") ?? "entrada");
  parametros.set("etapa", "acesso");

  return <header className="border-b border-foreground/10">
    <div className="mx-auto flex w-full max-w-5xl flex-wrap items-center justify-between gap-x-6 gap-y-2 px-4 py-3">
      <Link href="/prototipo" aria-label="UnDb — início do protótipo" className="py-2 text-xl font-semibold text-accent">UnDb <span className="text-xs font-normal text-foreground/60">protótipo</span></Link>
      <nav aria-label="Navegação do protótipo" className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm font-medium">
        <Link href="/prototipo" className="py-2 hover:text-accent hover:underline underline-offset-4">Buscar</Link>
        <Link href={`/prototipo?${parametros}`} aria-label="Conta do protótipo" className="rounded-lg border border-accent/30 px-4 py-2 text-accent hover:bg-accent/5">
          {estado === "visitante" ? "Entrar / Criar conta" : "Minha conta"}
        </Link>
        {estado !== "visitante" && <span className="text-xs text-foreground/70">{estado === "pendente" ? "E-mail não confirmado · simulação" : "E-mail confirmado · simulação"}</span>}
      </nav>
    </div>
  </header>;
}

export function AcessoParaAvaliar({ href }: { href: string }) {
  const { estado } = useContaDemo();
  return <div className="rounded-lg bg-foreground/[0.03] p-4 text-sm text-foreground/70">
    <p>{estado === "visitante"
      ? "Experimente a prévia sem conta. No sistema real, entre ou crie uma conta com e-mail confirmado para enviar."
      : estado === "pendente"
        ? "Seu cenário de conta ainda tem e-mail não confirmado. No sistema real, confirme o endereço antes de enviar. A prévia continua disponível."
        : "Cenário demonstrativo: conta com e-mail confirmado. Confira a prévia abaixo; nenhuma avaliação será enviada ou salva."}</p>
    <Link href={href} className="mt-2 inline-block text-sm text-accent underline underline-offset-4">{estado === "visitante" ? "Entrar ou criar conta para avaliar →" : "Ver minha conta →"}</Link>
  </div>;
}
